import logging
import argparse
import re
from apache_beam.options.pipeline_options import PipelineOptions
import apache_beam as beam

class RunTimeOptions(PipelineOptions):
    @classmethod
    def _add_argparse_args(cls, parser):
       parser.add_value_provider_argument(
           "--input_file_path",
           help="GCS Path of the input file"
       )
       parser.add_value_provider_argument(
           "--bq_table_id",
           help="datasetId.tableId"
       )

def deconcat(element):
    if ',' not in element[:10]:
        if element[0]=="9":
            element = element[:7]+','+element[7:]
        elif element[0]=="1":
            element = element[:8]+','+element[8:]
    return element


def replace_nulls(element):
    return element.replace('NULL','')

def format_datetime_bq(element):
    from datetime import datetime as dt

    ref = element.find('/20')
    start = element[:ref].rfind(',')+1
    end = ref+element[ref:].find(',')
    element = element[:start]+ dt.strftime( dt.strptime(element[start:end], '%m/%d/%Y %H:%M'),
                                          '%Y-%m-%d %H:%M:%S')+element[end:]

    rref = element.rfind('/20')
    start = element[:rref].rfind(',')+1
    end = rref+element[rref:].find(',')
    element = element[:start]+ dt.strftime( dt.strptime(element[start:end],'%m/%d/%Y %H:%M'),
                                          '%Y-%m-%d %H:%M:%S')+element[end:]

    return element

def parse_method(string_input):
    values = re.split(",", re.sub('\r\n', '', re.sub('"', '',string_input)))
    row = dict(
        zip(('Trip_Id', 'Trip__Duration', 'Start_Station_Id', 'Start_Time',
        'Start_Station_Name', 'End_Station_Id', 'End_Time', 'End_Station_Name',
        'Bike_Id', 'User_Type'),values))
    return row    

def run():
    """The main function which creates the pipeline and runs it."""

    pipeline_options = PipelineOptions(
        streaming=False, save_main_session=True, project='on-prem-project-337210', job_name='load-csv-gcs-bq'
    )

    p = beam.Pipeline(options=pipeline_options)
    user_options = pipeline_options.view_as(RunTimeOptions)

    (p
    | 'Read File' >> beam.io.ReadFromText(user_options.input_file_path)
    | 'Deconcactenate Columns' >> beam.Map(deconcat)
    | 'Replace Nulls' >> beam.Map(replace_nulls)
    | 'Convert to BQ Datetime' >> beam.Map(format_datetime_bq)
    | 'String To BigQuery Row' >> beam.Map(parse_method)
    | 'Write To BigQuery' >> beam.io.WriteToBigQuery(
    table=user_options.bq_table_id,
    schema='Trip_Id:INTEGER,Trip__Duration:INTEGER,Start_Station_Id:INTEGER,'
    'Start_Time:DATETIME,Start_Station_Name:STRING,End_Station_Id:INTEGER,'
    'End_Time:DATETIME, End_Station_Name:STRING, Bike_Id:INTEGER, User_Type:STRING',
    create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
    write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE))
    
    p.run().wait_until_finish()

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.WARNING)
    run()
