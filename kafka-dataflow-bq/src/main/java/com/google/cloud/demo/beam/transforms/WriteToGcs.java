package com.google.cloud.demo.beam.transforms;

import java.nio.charset.StandardCharsets;

import org.apache.avro.Schema;
import org.apache.avro.generic.GenericRecord;
import org.apache.avro.generic.GenericRecordBuilder;
import org.apache.beam.sdk.coders.AvroCoder;
import org.apache.beam.sdk.io.FileIO;
import org.apache.beam.sdk.io.parquet.ParquetIO;
import org.apache.beam.sdk.transforms.DoFn;
import org.apache.beam.sdk.transforms.windowing.AfterProcessingTime;
import org.apache.beam.sdk.transforms.windowing.FixedWindows;
import org.apache.beam.sdk.transforms.windowing.Repeatedly;
import org.apache.beam.sdk.transforms.windowing.Window;
import org.apache.beam.sdk.transforms.PTransform;
import org.apache.beam.sdk.transforms.ParDo;
import org.apache.beam.sdk.values.PCollection;
import org.apache.beam.sdk.values.PDone;
import org.apache.parquet.hadoop.metadata.CompressionCodecName;
import org.joda.time.Duration;

import com.google.cloud.demo.beam.MessageConsumerPipeline.MessageConsumerOptions;

public class WriteToGcs extends PTransform<PCollection<byte[]>, PDone> {

  final String outputFile;
  final Schema schema;
  final int windowIntervalInSeconds;
  final int numShards;

  public WriteToGcs(Schema schema, MessageConsumerOptions options) {
    this.schema = schema;
    this.outputFile = options.getOutputFile();
    this.windowIntervalInSeconds = options.getGcsWindowIntervalInSeconds();
    this.numShards = options.getGcsNumWriteShards();
  }

  static class ToGenericRecord extends DoFn<byte[], GenericRecord> {

    String schemaJson;
    Schema schema;
    
    public ToGenericRecord(Schema schema) {
      this.schemaJson = schema.toString();
    }

    @Setup
    public void setup() {
      this.schema = new Schema.Parser().parse(schemaJson);
    }

    @ProcessElement
    public void ProcessElement(ProcessContext c) {
      c.output(new GenericRecordBuilder(this.schema)
        .set("json", new String(c.element(), StandardCharsets.UTF_8))
        .build());
    }
  }

  @Override
  public PDone expand(PCollection<byte[]> logs) {
    PCollection<GenericRecord> records = logs
      // .apply("FixedWindows", Window.<byte[]>into(
      //   FixedWindows.of(Duration.standardSeconds(this.windowIntervalInSeconds))))
      .apply("FixedWindows", Window.<byte[]>into(
        FixedWindows.of(Duration.standardSeconds(this.windowIntervalInSeconds)))
          .triggering(Repeatedly.forever(AfterProcessingTime.pastFirstElementInPane()
            .plusDelayOf(Duration.standardSeconds(this.windowIntervalInSeconds))))
          .withAllowedLateness(Duration.standardSeconds(60))
          .discardingFiredPanes())
      .apply("ToGenericRecord", ParDo.of(new ToGenericRecord(schema)))
      .setCoder(AvroCoder.of(GenericRecord.class, this.schema));

    records.apply("WriteToFile", FileIO.<GenericRecord>write()
      .via(ParquetIO.sink(this.schema)
        .withCompressionCodec(CompressionCodecName.SNAPPY))
      .to(this.outputFile)
      .withSuffix(".parquet")
      .withNumShards(this.numShards));
    
    return PDone.in(logs.getPipeline());
  }
}
