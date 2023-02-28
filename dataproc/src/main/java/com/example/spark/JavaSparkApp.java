package com.example.spark;  

import java.util.Arrays;  
import java.util.Collection;  
import java.util.HashMap;  
import java.util.Map;  

import org.apache.kafka.clients.consumer.ConsumerRecord;  
import org.apache.spark.SparkConf;  
import org.apache.spark.streaming.Durations;  
import org.apache.spark.streaming.api.java.JavaDStream;  
import org.apache.spark.streaming.api.java.JavaInputDStream;  
import org.apache.spark.streaming.api.java.JavaStreamingContext;  
import org.apache.spark.streaming.kafka010.ConsumerStrategies;  
import org.apache.spark.streaming.kafka010.KafkaUtils;  
import org.apache.spark.streaming.kafka010.LocationStrategies;  
import org.apache.kafka.common.serialization.StringDeserializer;  

import org.apache.log4j.Level;  
import org.apache.log4j.Logger;  

public class JavaSparkApp {  
	public static void main(String[] args) throws InterruptedException {  
		// Firstly, we'll begin by initializing the JavaStreamingContext which is the entry point for all Spark Streaming applications:  
		Logger.getLogger("org").setLevel(Level.ALL);  
		Logger.getLogger("akka").setLevel(Level.ALL);  

		SparkConf sparkConf = new SparkConf();  
		sparkConf.setMaster("local");  
		sparkConf.set("spark.serializer", "org.apache.spark.serializer.KryoSerializer");  
		sparkConf.setAppName("KafkaStreaming");  

		JavaStreamingContext streamingContext = new JavaStreamingContext(sparkConf, Durations.seconds(1));  

		// Now, we can connect to the Kafka topic from the JavaStreamingContext.  
	
		Map<String, Object> kafkaParams = new HashMap<>();  
		kafkaParams.put("bootstrap.servers", "localhost:9092");  
		kafkaParams.put("key.deserializer", StringDeserializer.class);  
		kafkaParams.put("value.deserializer", StringDeserializer.class);  
		kafkaParams.put("auto.offset.reset", "latest");  
		kafkaParams.put("enable.auto.commit", false);  

		Collection<String> topics = Arrays.asList("kafka-topic");  

		JavaInputDStream<ConsumerRecord<String, String>> messages = KafkaUtils.createDirectStream(streamingContext, 
			LocationStrategies.PreferConsistent(),  
			ConsumerStrategies.<String, String>Subscribe(topics, kafkaParams));  
		JavaDStream<String> data = messages.map(v -> { return v.value(); });  
		
		data.print();  
		
		streamingContext.start();  
		streamingContext.awaitTermination();  
	}  
}  
