package com.google.cloud.demo.beam.utils;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;

import com.google.api.services.bigquery.model.TableRow;
import com.google.api.services.bigquery.model.TableSchema;

import org.apache.beam.sdk.io.gcp.bigquery.BigQueryIO;
import org.apache.beam.sdk.io.gcp.bigquery.BigQueryIO.Write;
import org.apache.beam.sdk.io.gcp.bigquery.TableRowJsonCoder;
import org.apache.beam.sdk.coders.Coder.Context;

import org.joda.time.Duration;

import com.google.cloud.demo.beam.MessageConsumerPipeline.MessageConsumerOptions;

public class BigQueryUtil {

  static public Write<byte[]> expandBigQueryWrite(TableSchema schema, MessageConsumerOptions options) {
    Write<byte[]> bigQueryWrite = BigQueryIO.<byte[]>write()
      .withFormatFunction(c -> convertJsonToTableRow(c))
      .to(options.getOutputTable())
      .withSchema(schema)
      .withCreateDisposition(BigQueryIO.Write.CreateDisposition.CREATE_IF_NEEDED)
      .withWriteDisposition(BigQueryIO.Write.WriteDisposition.WRITE_APPEND);
    
    if (options.getBigQueryWriteMethod().equals("storage_write")) {
      bigQueryWrite = bigQueryWrite
        .withMethod(BigQueryIO.Write.Method.STORAGE_WRITE_API);
    }
    else if (options.getBigQueryWriteMethod().equals("streaming_insert")) {
      bigQueryWrite = bigQueryWrite
        .withMethod(BigQueryIO.Write.Method.STREAMING_INSERTS);
    }
    else if (options.getBigQueryWriteMethod().equals("load_job")) {
      bigQueryWrite = bigQueryWrite
        .withMethod(BigQueryIO.Write.Method.FILE_LOADS);
    }

    if (options.getBigQueryUseAutoSharding()) {
      bigQueryWrite = bigQueryWrite
        .withAutoSharding();
    }
    else {
      bigQueryWrite = bigQueryWrite
        .withNumStorageWriteApiStreams(options.getBigQueryNumWriteStreams())
        .withTriggeringFrequency(Duration.standardSeconds(options.getBigQueryWriteTriggerSeconds()));
    }

    return bigQueryWrite;
  }

  public static TableRow convertJsonToTableRow(byte[] bytes) {
    TableRow row;
    try (InputStream inputStream =
        new ByteArrayInputStream(bytes)) {
      row = TableRowJsonCoder.of().decode(inputStream, Context.OUTER);

    } catch (IOException e) {
      throw new RuntimeException("Failed to serialize json to table row: "
        + new String(bytes, StandardCharsets.UTF_8), e);
    }
    return row;
  }
}
