from apache_beam.options.pipeline_options import PipelineOptions
from google.cloud import pubsub_v1
from google.cloud import bigquery
import apache_beam as beam
from apache_beam.io import ReadFromText
from apache_beam import window
import logging
import argparse
import sys
import re
import json
import random
from apache_beam.transforms.window import FixedWindows
from apache_beam import DoFn, GroupByKey, io, ParDo, Pipeline, PTransform, WindowInto, WithKeys
from datetime import datetime, timedelta
import time

PROJECT="on-prem-project-337210"
schema = "client_id:STRING, \
    epoch_time:STRING, \
    properties_session_source:STRING, \
    properties_session_id:STRING, \
    properties_item_publisher_id:STRING, \
    properties_user_handset_maker:STRING, \
    properties_session_start_time:STRING, \
    properties_user_os_platform:STRING, \
    properties_item_type:STRING, \
    properties_user_connection:STRING, \
    properties_user_language_primary:STRING, \
    properties_user_handset_model:STRING, \
    properties_referrer:STRING, \
    properties_item_id:STRING, \
    properties_referrer_id:STRING, \
    properties_referrer_action:STRING, \
    properties_item_language:STRING, \
    properties_card_position:INTEGER, \
    properties_card_type:STRING, \
    properties_depth:STRING, \
    properties_req_id:STRING, \
    properties_current_pull_id:STRING, \
    properties_days_since_activation:STRING, \
    properties_sourcetype:STRING, \
    properties_enriched_user_id:STRING, \
    properties_type:STRING, \
    properties_post_type:STRING, \
    properties_subformat:STRING, \
    properties_fg_session_count:INTEGER, \
    properties_fg_session_id:STRING, \
    properties_enriched_state:STRING, \
    properties_timespent:FLOAT, \
    properties_campaign_type:STRING, \
    properties_fg_session_duration:INTEGER, \
    properties_ftd_session_time:INTEGER, \
    properties_ftd_session_count:INTEGER, \
    properties_reco_v_card_position:STRING, \
    properties_latitute:STRING, \
    properties_imagecount:INTEGER, \
    properties_handset_model_id:STRING, \
    properties_is_clicked:BOOLEAN, \
    properties_timespent_array:STRING, \
    properties_user_id:STRING, \
    properties_location:STRING, \
    properties_is_followed_source:STRING, \
    properties_reco_api_id:STRING, \
    properties_is_liked:STRING, \
    properties_is_shared:STRING, \
    properties_user_region:STRING"
TOPIC = "projects/on-prem-project-337210/topics/verse"

def flatten_data(y):
    out = {}
    row = json.loads(y)
    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(row)
    return out

def parse_json(element):
    new_json = {}
    #json_cols = ['event_section','user_id','ts_time_druid']
    json_cols=[ "client_id",
                "epoch_time",
                "properties_session_source",
                "properties_session_id",
                "properties_item_publisher_id",
                "properties_user_handset_maker",
                "properties_session_start_time",
                "properties_user_os_platform",
                "properties_item_type",
                "properties_user_connection",
                "properties_user_language_primary",
                "properties_user_handset_model",
                "properties_referrer",
                "properties_item_id",
                "properties_referrer_id",
                "properties_referrer_action",
                "properties_item_language",
                "properties_card_position",
                "properties_card_type",
                "properties_depth",
                "properties_req_id",
                "properties_current_pull_id",
                "properties_days_since_activation",
                "properties_sourcetype",
                "properties_enriched_user_id",
                "properties_type",
                "properties_post_type",
                "properties_subformat",
                "properties_fg_session_count",
                "properties_fg_session_id",
                "properties_enriched_state",
                "properties_timespent",
                "properties_campaign_type",
                "properties_fg_session_duration",
                "properties_ftd_session_time",
                "properties_ftd_session_count",
                "properties_reco_v_card_position",
                "properties_latitute",
                "properties_imagecount",
                "properties_handset_model_id",
                "properties_is_clicked",
                "properties_timespent_array",
                "properties_user_id",
                "properties_location",
                "properties_is_followed_source",
                "properties_reco_api_id",
                "properties_is_liked",
                "properties_is_shared",
                "properties_user_region",
                "properties_item_category_id",
                "properties_longitude",
                "properties_latitude",
                "properties_event_attribution",
                "properties_user_segment",
                "properties_user_feed_logic",
                "properties_topics",
                "properties_event_attribution_id",
                "properties_tab_index",
                "properties_page_number",
                "properties_tab_name",
                "properties_tab_id",
                "properties_item_tag_id",
                "properties_item_tag_ids",
                "properties_pagenumber",
                "properties_group_type",
                "properties_content_type",
                "properties_candidate_size",
                "properties_target_user_id"
                ]
    for i in json_cols:
        new_json[i] = element.get(i)
    new_json = json.dumps(new_json)
    #print(new_json)
    return json.loads(new_json)

class GroupMessagesByFixedWindows(PTransform):
    """A composite transform that groups Pub/Sub messages based on publish time
    and outputs a list of tuples, each containing a message and its publish time.
    """

    def __init__(self, window_size, num_shards=5):
        # Set window size to 60 seconds.
        self.window_size = int(window_size * 60)
        self.num_shards = num_shards

    def expand(self, pcoll):
        import random
        import apache_beam as beam
        return (
            pcoll
            # Bind window info to each element using element timestamp (or publish time).
            | "Window into fixed intervals"
            >> WindowInto(FixedWindows(self.window_size))
            | "Add timestamp to windowed elements" >> ParDo(AddTimestamp())
            # Assign a random key to each windowed element based on the number of shards.
            | "Add key" >> WithKeys(lambda _: random.randint(0, self.num_shards - 1))
            # Group windowed elements by key. All the elements in the same window must fit
            # memory for this. If not, you need to use `beam.util.BatchElements`.
            | "Group by key" >> GroupByKey()
        )


class AddTimestamp(DoFn):
    def process(self, element, publish_time=DoFn.TimestampParam):
        import time
        import apache_beam as beam
        unix_timestamp = int(time.time())
        yield beam.window.TimestampedValue(element, unix_timestamp)

class WriteToGCS(DoFn):
    def __init__(self, output_path):
        self.output_path = output_path

    def process(self, key_value, window=DoFn.WindowParam):
        from apache_beam import io
        """Write messages in a batch to Google Cloud Storage."""

        ts_format = "%H:%M"
        window_start = window.start.to_utc_datetime().strftime(ts_format)
        window_end = window.end.to_utc_datetime().strftime(ts_format)
        shard_id, batch = key_value
        filename = "-".join([self.output_path, window_start, window_end, str(shard_id)])

        with io.gcsio.GcsIO().open(filename=filename, mode="w") as f:
            for message_body in batch:
                f.write(f"{message_body}\n".encode("utf-8"))



def main(argv=None):

   parser = argparse.ArgumentParser()
   parser.add_argument("--input_topic")
   parser.add_argument("--output")
   known_args = parser.parse_known_args(argv)


   p = beam.Pipeline(options=PipelineOptions())

   datasource = (p
      | 'ReadData' >> beam.io.ReadFromPubSub(topic=TOPIC).with_output_types(bytes)
      | "Flatten JSON" >> beam.Map(flatten_data)
      | "Json Parser" >> beam.Map(parse_json)
   )

   bq_streaming_write = (datasource
      | 'WriteToBigQuery' >> beam.io.WriteToBigQuery('{0}:dataflow_python.logdata'.format(PROJECT), schema=schema,
        write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND)
   )

   gcs_files_write = (datasource
      | "Window into" >> GroupMessagesByFixedWindows(1.0, 5)
      | "Write to GCS" >> ParDo(WriteToGCS("gs://customer-demos-asia-south1/dataflow/output.jsonl"))   
   )

   result = p.run()
   result.wait_until_finish()

if __name__ == '__main__':
  logger = logging.getLogger().setLevel(logging.INFO)
  main()
