
import apache_beam as beam
from google.cloud import pubsub_v1
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions
from apache_beam.io import ReadFromText
from apache_beam.io import fileio, filesystem
from apache_beam.transforms.window import FixedWindows
from apache_beam import DoFn, GroupByKey, io, ParDo, Pipeline, PTransform, WindowInto, WithKeys, GroupBy
from apache_beam.transforms.trigger import AccumulationMode
from apache_beam.transforms.trigger import AfterProcessingTime
import pyarrow as pa
import logging
import json
import random

TOPIC = "projects/on-prem-project-337210/topics/parquet"

class ParquetSink(beam.io.fileio.FileSink):
    def __init__(self,
                file_path_prefix,
                schema,
                row_group_buffer_size=64 * 1024 * 1024,
                record_batch_size=1000,
                codec='none',
                use_deprecated_int96_timestamps=False,
                use_compliant_nested_type=False,
                file_name_suffix='',
                num_shards=3,
                shard_name_template=None,
                mime_type='application/x-parquet'):
        self._inner_sink = beam.io.parquetio._create_parquet_sink(
            file_path_prefix,
            schema,
            codec,
            row_group_buffer_size,
            record_batch_size,
            use_deprecated_int96_timestamps,
            use_compliant_nested_type,
            file_name_suffix,
            num_shards,
            shard_name_template,
            mime_type
        )
        self._codec = codec
        self._schema = schema
        self._use_deprecated_int96_timestamps = use_deprecated_int96_timestamps

    def open(self, fh):
        self._pw = pa.parquet.ParquetWriter(
            fh,
            self._schema,
            compression=self._codec,
            use_deprecated_int96_timestamps=self._use_deprecated_int96_timestamps)

    def write(self, record):
        self._inner_sink.write_record(self._pw, record)

    def flush(self):
        if len(self._inner_sink._buffer[0]) > 0:
            self._inner_sink._flush_buffer()
        if self._inner_sink._record_batches_byte_size > 0:
            self._inner_sink._write_batches(self._pw)

        self._pw.close()

def parquet_compatible_filenaming(suffix=None):
    def _inner(window, pane, shard_index, total_shards, compression, destination):
        return fileio.destination_prefix_naming(suffix )(
            window, pane, shard_index, total_shards, compression, destination).replace(":", ".")

    return _inner

schema = pa.schema([
    pa.field('properties_cis_enriched_item_channel_id', pa.string()),
    pa.field('properties_enriched_client_ip', pa.string()),
    pa.field('properties_referrer_id', pa.string())
])

def run(argv=None, save_main_session=True):

    #p = beam.Pipeline(options=PipelineOptions())
    pipeline_options = PipelineOptions()
    pipeline_options.view_as(SetupOptions).save_main_session = save_main_session
    with beam.Pipeline(options=pipeline_options) as p:    

        datasource = (p
        | 'ReadData' >> beam.io.ReadFromPubSub(topic=TOPIC).with_output_types(bytes)
        | "Parse JSON" >> beam.Map(json.loads)
        | "Window into fixed intervals" >> WindowInto(FixedWindows(60))
        | "Group by key" >> GroupBy(lambda s: random.randint(0, 2))
        | 'Extract Values"' >> beam.FlatMap(lambda x: x[1])
        | 'Write to Parquet' >> fileio.WriteToFiles(
                                    path=str("gs://customer-demos-asia-south1/dataflow/"),
                                    #destination=lambda x: x["some_key"],
                                    sink=lambda x: ParquetSink(
                                                        file_path_prefix="output",
                                                        file_name_suffix=".parquet",
                                                        codec="snappy",
                                                        schema=schema,
                                                        mime_type='application/x-parquet',
                                                        num_shards=3),
                                    file_naming=parquet_compatible_filenaming(suffix=".parquet")
                                    )
        )

    result = p.run()
    result.wait_until_finish()

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.WARNING)
    run()
