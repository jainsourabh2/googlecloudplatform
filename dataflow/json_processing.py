import logging
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.io import ReadFromText
import json  

def custom_json_parser(element):
    new_json = {}
    new_json['event_section'] = element['event_section']
    return new_json

def run():
    projectId='on-prem-project-337210'
    datasetId='demo'
    table_schema = 'event_section:STRING,user_id:STRING,ts_time_druid:STRING,epoch_time_original:INTEGER,ts_day_hour:STRING,tertrtclient_id:STRING,client_ip:STRING,ts_day:DATE,event_name:STRING,epoch_time:STRING,et_day_hour:STRING,et_day:STRING'

    options = PipelineOptions()
    p = beam.Pipeline(options=options)

    data_from_source = (p
                    #| "READ FROM JSON" >> ReadFromText("gs://customer-demos-asia-south1/dataflow/input.json")
                    | "READ FROM JSON" >> ReadFromText("/home/admin_sourabhsjain_altostrat_com/dataflow-python/input.json")
                    | "PARSE JSON" >> beam.Map(json.loads)
                    | "CUSTOM JOSN PARSE" >> beam.Map(custom_json_parser)
                    |"WriteToBigQuery" >> beam.io.WriteToBigQuery(
                        "{0}:{1}.table_name".format(projectId, datasetId),
                        schema=table_schema,
                        write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                        create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
                    )
    )

    result = p.run()

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.WARNING)
    run()
