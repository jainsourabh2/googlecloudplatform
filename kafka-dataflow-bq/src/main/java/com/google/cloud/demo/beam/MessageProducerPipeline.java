package com.google.cloud.demo.beam;

import com.google.cloud.demo.model.LogMessage;
import com.google.gson.Gson;

import org.apache.beam.sdk.Pipeline;
import org.apache.beam.sdk.io.GenerateSequence;
import org.apache.beam.sdk.io.kafka.KafkaIO;
import org.apache.beam.sdk.options.Default;
import org.apache.beam.sdk.options.Description;
import org.apache.beam.sdk.options.PipelineOptionsFactory;
import org.apache.beam.sdk.transforms.DoFn;
import org.apache.beam.sdk.transforms.ParDo;
import org.apache.kafka.common.serialization.ByteArraySerializer;
import org.apache.beam.runners.dataflow.options.DataflowPipelineOptions;
import org.joda.time.Duration;

import java.util.Map;
import java.util.Random;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;

public class MessageProducerPipeline {

  public interface MessageProducerOptions extends DataflowPipelineOptions {
    @Description("Number of messages to generate per interval.")
    @Default.Long(10000L)
    long getNumMessages();
    void setNumMessages(long numMessages);

    @Description("Interval duration in seconds.")
    @Default.Long(1L)
    long getIntervalInSeconds();
    void setIntervalInSeconds(long intervalInSeconds);

    @Description("Kafka bootstrap servers.")
    String getBootstrapServers();
    void setBootstrapServers(String boostrapServers);

    @Description("Kafka topic.")
    String getTopic();
    void setTopic(String topic);

    // FOR TESTING ONLY

    @Description("Kafka username.")
    String getUsername();
    void setUsername(String username);

    @Description("Kafka password.")
    String getPassword();
    void setPassword(String password);

    // FOR TESTING ONLY
  }

  static class GenerateMessage extends DoFn<Long, byte[]> {
    Random rand = null;
    Gson gson = null;

    @DoFn.Setup
    public void setup() {
      gson = new Gson();
      rand = new Random();
    }

    @DoFn.ProcessElement
    public void processElement(ProcessContext c) {
      LogMessage msg = new LogMessage.Builder()
          .setRequestId(Integer.toString(rand.nextInt()))
          .setResponseTime(rand.nextInt(1000))
          .setRequestMethod("GET")
          .setRequestUrl("/api/load-test")
          .setResponseCode(200)
          .setResponseMessage("OK")
          .setRequestPayload(new LogMessage.RequestPayload.Builder()
              .setUserId(rand.nextInt(1000000))
              .setAction("start_load_test")
              .build())
          .setServerIP("192.169.1.100")
          .setUserAgent("load-test-client-1.0")
          .build();

      String json = gson.toJson(msg);
      c.output(json.getBytes(StandardCharsets.UTF_8));
    }
  }

  static Map<String, Object> getConsumerProperties(MessageProducerOptions options) {
    Map<String, Object> props = new HashMap<>();
    props.put("compression.type", "gzip");
    props.put("sasl.mechanism", "PLAIN");
    props.put("sasl.jaas.config","org.apache.kafka.common.security.plain.PlainLoginModule required username=\""
      + options.getUsername() + "\" password=\"" + options.getPassword() + "\";");
    props.put("security.protocol", "SASL_PLAINTEXT");
    return props;
  }

  public static void main(String[] args) {

    MessageProducerOptions options =
        PipelineOptionsFactory.fromArgs(args).withValidation().as(MessageProducerOptions.class);
    Map<String, Object> props = getConsumerProperties(options);
    Pipeline p = Pipeline.create(options);

    p.apply(
        "Tick", GenerateSequence.from(0).withRate(options.getNumMessages(), Duration.standardSeconds(1L)))
     .apply(
        "GenerateMessage", ParDo.of(new GenerateMessage())
     );
    //  .apply("WriteToTopic", KafkaIO.<Void, byte[]>write()
    //     .withBootstrapServers(options.getBootstrapServers())
    //     .withTopic(options.getTopic())
    //     .withValueSerializer(ByteArraySerializer.class)
    //     .withProducerConfigUpdates(props)
    //     .values());

    p.run().waitUntilFinish();
  }
}
