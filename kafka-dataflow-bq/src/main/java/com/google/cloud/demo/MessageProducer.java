package com.google.cloud.demo;

import com.google.cloud.demo.model.LogMessage;

import com.google.gson.Gson;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;

import org.apache.kafka.clients.producer.Producer;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.clients.producer.ProducerConfig;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;
import java.util.Random;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MessageProducer {

  static final String KAFKA_SERIALIZER_CLASS =
    "org.apache.kafka.common.serialization.ByteArraySerializer";
  static final String KAFKA_DESERIALIZER_CLASS =
    "org.apache.kafka.common.serialization.ByteArrayDeserializer";

  static final Logger log = LoggerFactory.getLogger(MessageProducer.class);

  final Producer <byte[], byte[]> producer;

  Random rand = new Random();
  Gson gson = new Gson();

  public MessageProducer(Properties properties) {
    producer = new KafkaProducer<>(properties);
  }

  public void startLoop(String topic, Long intervalInMs,
      Long numRecords) throws InterruptedException {

    Runtime.getRuntime().addShutdownHook(new Thread(() -> {
      producer.flush();
      producer.close();
    }));
    
    log.info("Starting main processing loop ...");

    while (true) {
      for (int i=0; i<numRecords; i++) {
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
        ProducerRecord<byte[], byte[]> record = new ProducerRecord<byte[],byte[]>(
          topic, json.getBytes());
        producer.send(record);
      }
      log.info("Sent " + Long.toString(numRecords) + "messages.");
      Thread.sleep(intervalInMs);
    }
  }

  static CommandLine parseArgs(String[] args) {
    Options options = new Options();
    
    Option bootstrapServers = new Option("bootstrapServers", true,
      "Kafka bootstrap servers to use");
    options.addOption(bootstrapServers);
    
    Option config = new Option("config", true,
      "Kafka producer config file");
    options.addOption(config);

    Option topic = new Option("topic", true,
      "Kafka topic");
    topic.setRequired(true);
    options.addOption(topic);

    Option numRecords = new Option("numRecords", true, 
      "Number of messages to send per interval");
    numRecords.setRequired(true);
    numRecords.setType(Long.class);
    options.addOption(numRecords);

    Option intervalInMs = new Option("intervalInMs", true,
      "Number of ms to wait between generating each record batch");
    intervalInMs.setType(Long.class);
    options.addOption(intervalInMs);

    CommandLineParser parser = new DefaultParser();
    HelpFormatter formatter = new HelpFormatter();

    try {
      return parser.parse(options, args);
    } catch (ParseException e) {
      System.out.println(e.getMessage());
      formatter.printHelp("MessageProducer", options);
    }

    return null;
  }

  public static void main(String[] args) throws IOException, InterruptedException {
    CommandLine cmdLine = parseArgs(args);
    if (cmdLine != null) {
      String bootstrapServers = cmdLine.getOptionValue("bootstrapServers");
      Long numRecords = Long.parseLong(
        cmdLine.getOptionValue("numRecords", Long.toString(1000L)));
      Long intervalInMs = Long.parseLong(
        cmdLine.getOptionValue("intervalInMs", Long.toString(1L)));
      String configFile = cmdLine.getOptionValue("config");
      String topic = cmdLine.getOptionValue("topic");

      Properties properties = new Properties();

      if (configFile != null) {
        log.info("Reading Kafka producer config file");
        try (InputStream input = new FileInputStream(configFile)) {
          properties.load(input);
        }
      }
  
      if (bootstrapServers != null) {
        log.info("Using bootstrap servers value from parameters");
        properties.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
      }
  
      properties.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, KAFKA_SERIALIZER_CLASS);
      properties.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, KAFKA_SERIALIZER_CLASS);
  
      MessageProducer msgProducer = new MessageProducer(properties);
      msgProducer.startLoop(topic, intervalInMs, numRecords);
    }
  }
}
