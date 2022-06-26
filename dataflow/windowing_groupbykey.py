import logging
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions,StandardOptions
from apache_beam.io.kafka import ReadFromKafka
from apache_beam.io.kafka import WriteToKafka
from apache_beam.io import ReadFromText
from apache_beam import window
from apache_beam.transforms.trigger import AfterWatermark, AfterProcessingTime, AccumulationMode, AfterCount
import json
import time    
import random
from datetime import datetime, timedelta

bootstrap_servers = '100.90.1.220:9092'

topic = 'analytics_news_story_card_views'
with_metadata = False

class AddTimestampDoFn(beam.DoFn):
  def process(self, element):
    # Extract the numeric Unix seconds-since-epoch timestamp to be
    # associated with the current log entry.
    # unix_timestamp = extract_timestamp_from_log_entry(element)
    unix_timestamp = int(time.time())
    # Wrap and emit the current entry and new timestamp in a
    # TimestampedValue.
    yield beam.window.TimestampedValue(element, unix_timestamp)

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

def run():
    projectId='et-gcp-aiml-sandbox'
    datasetId='aiml_raw'
    #table_schema = 'event_section:STRING,user_id:STRING,ts_time_druid:STRING,epoch_time_original:INTEGER,ts_day_hour:STRING,tertrtclient_id:STRING,client_ip:STRING,ts_day:DATE,event_name:STRING,epoch_time:STRING,et_day_hour:STRING,et_day:STRING'
    table_schema = "client_id:STRING, \
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
    properties_user_region:STRING "

    options = PipelineOptions()
    p = beam.Pipeline(options=options)

    data_from_source = (p
                    | "Read from JSON" >> ReadFromText("./input_1.jsonl")
                    | "Add Timestamp" >> beam.ParDo(AddTimestampDoFn())
                    | "Flatten JSON" >> beam.Map(flatten_data)
                    | "Json Parser" >> beam.Map(parse_json)
                    | "Map Key" >> beam.WithKeys(lambda msg: msg["properties_session_source"])
                    | "Window Operation" >> beam.WindowInto(window.FixedWindows(300))
                    | "Group counts" >> beam.GroupByKey()
                    | "Print" >> beam.MapTuple(lambda k,v: print(len(v)))
                    | "Post Grouping Operation" >> beam.MapTuple(lambda key,arr:{"key":key,"sum": sum(val["properties_card_position"] for val in arr)})
                    | "File Output" >> beam.io.WriteToText("./sample.jsonl")
                    )

    result = p.run()

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.WARNING)
    run()
