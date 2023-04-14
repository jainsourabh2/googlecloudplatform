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
import org.apache.beam.sdk.transforms.FlatMapElements;
import org.apache.beam.sdk.transforms.ParDo;
import org.apache.beam.sdk.transforms.Reshuffle;
import org.apache.beam.sdk.transforms.SimpleFunction;
import org.apache.kafka.common.serialization.ByteArraySerializer;
import org.apache.beam.runners.dataflow.options.DataflowPipelineOptions;
import org.joda.time.Duration;

import java.util.Map;
import java.util.Random;
import java.util.Collections;
import java.util.HashMap;
import java.util.stream.LongStream;

public class MessageFanoutProducerPipeline {

  public interface MessageProducerOptions extends DataflowPipelineOptions {
    @Description("Multiple of 10000 messages to publish per second.")
    @Default.Long(200L)
    long getNum10KMessages();
    void setNum10KMessages(long numMessages);

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
  }

  static class GenerateMessage extends DoFn<Void, byte[]> {
    final Long numMessages;
    Random rand = null;
    Gson gson = null;

    public GenerateMessage(Long numMessages) {
      this.numMessages = numMessages;
    }

    @DoFn.Setup
    public void setup() {
      gson = new Gson();
      rand = new Random();
    }

    private byte[] newMessage() {
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

      return gson.toJson(msg).getBytes();
    }

    @DoFn.ProcessElement
    public void processElement(ProcessContext c) {
      LongStream.range(0, numMessages)
        .forEach(unused -> c.output(newMessage()));
    }
  }

  static Map<String, Object> getConsumerProperties(MessageProducerOptions options) {
    Map<String, Object> props = new HashMap<>();
    props.put("compression.type", "gzip");
    return props;
  }

  public static void main(String[] args) {

    MessageProducerOptions options =
        PipelineOptionsFactory.fromArgs(args).withValidation().as(MessageProducerOptions.class);
    Map<String, Object> props = getConsumerProperties(options);
    Pipeline p = Pipeline.create(options);

    p.apply(
        "Tick", GenerateSequence.from(0).withRate(10L, Duration.standardSeconds(1L)))
     .apply("ReshuffleTick", Reshuffle.viaRandomKey())
     .apply("FanoutMultiplier", FlatMapElements.via(new SimpleFunction<Long, Iterable<Void>>() {
        @Override
        public Iterable<Void> apply(Long input) {
          return Collections.nCopies(1000, null);
        }
       }))
     .apply("ReshuffleMultiplier", Reshuffle.viaRandomKey())
     .apply("GenerateMessages", ParDo.of(new GenerateMessage(options.getNum10KMessages())))
     .apply("WriteToTopic", KafkaIO.<Void, byte[]>write()
        .withBootstrapServers(options.getBootstrapServers())
        .withTopic(options.getTopic())
        .withValueSerializer(ByteArraySerializer.class)
        .withProducerConfigUpdates(props)
        .values());

    p.run().waitUntilFinish();
  }
}
