package com.google.cloud.demo.beam;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.apache.beam.sdk.Pipeline;
import org.apache.beam.runners.dataflow.options.DataflowPipelineOptions;
import org.apache.beam.sdk.io.kafka.KafkaIO;
import org.apache.beam.sdk.options.Default;
import org.apache.beam.sdk.options.Description;
import org.apache.beam.sdk.options.PipelineOptionsFactory;
import org.apache.beam.sdk.transforms.MapElements;
import org.apache.beam.sdk.transforms.Reshuffle;
import org.apache.beam.sdk.transforms.Values;
import org.apache.beam.sdk.values.PCollection;
import org.apache.beam.sdk.values.TypeDescriptor;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.common.serialization.ByteArrayDeserializer;
import org.apache.kafka.common.serialization.VoidDeserializer;

import com.google.api.services.bigquery.model.TableFieldSchema;
import com.google.api.services.bigquery.model.TableRow;
import com.google.api.services.bigquery.model.TableSchema;
import com.google.cloud.demo.beam.utils.BigQueryUtil;

public class MessageConsumerPipeline {

  public interface MessageConsumerOptions extends DataflowPipelineOptions {
    @Description("Kafka bootstrap servers.")
    String getBootstrapServers();

    void setBootstrapServers(String boostrapServers);

    @Description("Kafka topic.")
    String getTopic();

    void setTopic(String topic);

    @Description("Kafka consumer group id.")
    @Default.String("message-consumer-pipeline")
    String getGroupId();
    void setGroupId(String groupId);

    @Description("BigQuery fully-qualified output table.")
    String getOutputTable();
    void setOutputTable(String outputTable);

    @Description("BigQuery Storage Write API triggering frequency in seconds.")
    @Default.Integer(5)
    int getBigQueryWriteTriggerSeconds();
    void setBigQueryWriteTriggerSeconds(int bigQueryWriteTriggerSeconds);

    @Description("Number of BigQuery Storage Write API streams.")
    @Default.Integer(2000)
    int getBigQueryNumWriteStreams();
    void setBigQueryNumWriteStreams(int bigQueryNumWriteStreams);

    @Description("Sink type.")
    @Default.String("bigquery")
    String getSinkType();
    void setSinkType(String sinkType);

    @Description("The method to use for writing to BigQuery. Values are 'storage_write', 'streaming_insert', 'load_job'.")
    @Default.String("storage_write")
    String getBigQueryWriteMethod();
    void setBigQueryWriteMethod(String bigQueryWriteMethod);

    @Description("Number of BigQuery Storage Write API streams.")
    @Default.Integer(500)
    int getNumReshuffleBuckets();
    void setNumReshuffleBuckets(int numReshuffleBuckets);

    @Description("Whether to use BigQuery write autosharding.")
    @Default.Boolean(true)
    boolean getBigQueryUseAutoSharding();
    void setBigQueryUseAutoSharding(boolean bigQueryUseAutoSharding);

    @Description("Output file location if using sinkType=gcs.")
    String getOutputFile();
    void setOutputFile(String outputFile);

    @Description("The window interval in seconds to use for writes if using sinkType=gcs.")
    @Default.Integer(60)
    int getGcsWindowIntervalInSeconds();
    void setGcsWindowIntervalInSeconds(int windowIntervalInSeconds);

    @Description("The number of write shards to GCS.")
    @Default.Integer(1000)
    int getGcsNumWriteShards();
    void setGcsNumWriteShards(int gcsNumWriteShards);
  }

  static TableSchema getBigQuerySchema() {
    List<TableFieldSchema> requestPayloadFields = new ArrayList<>();
    requestPayloadFields.add(new TableFieldSchema()
      .setName("action")
      .setType("STRING")
      .setMode("REQUIRED"));
    requestPayloadFields.add(new TableFieldSchema()
      .setName("userId")
      .setType("INT64")
      .setMode("REQUIRED"));

    List<TableFieldSchema> fields = new ArrayList<>();
    fields.add(new TableFieldSchema()
      .setName("requestId")
      .setType("STRING")
      .setMode("REQUIRED"));
    fields.add(new TableFieldSchema()
      .setName("requestMethod")
      .setType("STRING")
      .setMode("REQUIRED"));
    fields.add(new TableFieldSchema()
      .setName("requestPayload")
      .setType("RECORD")
      .setFields(requestPayloadFields));
    fields.add(new TableFieldSchema()
      .setName("responseCode")
      .setType("INT64")
      .setMode("REQUIRED"));
    fields.add(new TableFieldSchema()
      .setName("responseMessage")
      .setType("STRING")
      .setMode("REQUIRED"));
    fields.add(new TableFieldSchema()
      .setName("responseTime")
      .setType("INT64")
      .setMode("REQUIRED"));
    fields.add(new TableFieldSchema()
      .setName("serverIP")
      .setType("STRING")
      .setMode("REQUIRED"));
    fields.add(new TableFieldSchema()
      .setName("userAgent")
      .setType("STRING")
      .setMode("REQUIRED"));

    return new TableSchema().setFields(fields);
  }

  static Map<String, Object> getConsumerConfig(MessageConsumerOptions options) {
    Map<String, Object> props = new HashMap<>();
    props.put(ConsumerConfig.GROUP_ID_CONFIG, options.getGroupId());
    return props;
  }

  public static void main(String[] args) {

    MessageConsumerOptions options = PipelineOptionsFactory.fromArgs(args).withValidation()
        .as(MessageConsumerOptions.class);
    options.setStreaming(true);
    
    final Map<String, Object> props = getConsumerConfig(options);
    final TableSchema bqSchema = getBigQuerySchema();

    Pipeline p = Pipeline.create(options);
    PCollection<byte[]> logs = p.apply(
        "ReadFromTopic", KafkaIO.<Void, byte[]>read()
            .withBootstrapServers(options.getBootstrapServers())
            .withTopic(options.getTopic())
            .withKeyDeserializer(VoidDeserializer.class)
            .withValueDeserializer(ByteArrayDeserializer.class)
            .withConsumerConfigUpdates(props)
            .withoutMetadata())
        .apply("Values", Values.create());

    if (options.getSinkType().equals("bigquery")) {
      logs.apply("WriteToBigQuery", BigQueryUtil.expandBigQueryWrite(bqSchema, options));
    }
    else if (options.getSinkType().equals("reshuffle")) {
      logs
        .apply("JsonToTableRows", MapElements
            .into(TypeDescriptor.of(TableRow.class))
            .via(c -> BigQueryUtil.convertJsonToTableRow(c)))
        .apply("Reshuffle", Reshuffle.<TableRow>viaRandomKey()
          .withNumBuckets(options.getNumReshuffleBuckets()));
    }

    p.run();
  }
}
