import logging
import argparse
import re
from datetime import datetime as dt
from apache_beam.options.pipeline_options import PipelineOptions
import apache_beam as beam

def deconcat(element):
    """This function takes a string with comma separated values as input and
    separates first two values with a comma if they are concatenated.
    Args:
    string_input:A comma separated values in the form:
    'Trip_IdTrip__Duration, Start_Station_Id, Start_Time, Start_Station_Name,
    End_Station_Id, End_Time, End_Station_Name, Bike_Id, User_Type'
    Example string_input: '10000083720,7239,2020-03-10 13:28:00,
    Bloor St W / Manning Ave - SMART,7160,10/03/2020 13:40,
    King St W / Tecumseth St,5563,Annual Member'
    Returns:
    A string comma separated values in the form:
    'Trip_Id, Trip__Duration, Start_Station_Id, Start_Time, Start_Station_Name,
    End_Station_Id, End_Time, End_Station_Name, Bike_Id, User_Type'
    Example string_output: '10000083,720,7239,2020-03-10 13:28:00,
    Bloor St W / Manning Ave - SMART,7160,10/03/2020 13:40,
    King St W / Tecumseth St,5563,Annual Member'
    """
    if ',' not in element[:10]:
        if element[0]=="9":
            element = element[:7]+','+element[7:]
        elif element[0]=="1":
            element = element[:8]+','+element[8:]
    return element

def replace_nulls(element):
    """This function takes a string with comma separated values as input and
    replaces all NULL values with an and empty string
    Example input string:
    '10000085,1526,7239,10/03/2020 13:28,Bloor St W / Manning Ave - SMART,NULL,
    10/03/2020 13:53,Foster Pl / Elizabeth St - SMART,3956,Annual Member'
    Example output string:
    '10000083,720,7239,2020-10-03 13:28:00,Bloor St W / Manning Ave - SMART,,
    2020-10-03 13:40:00,King St W / Tecumseth St,5563,Annual Member'
    """
    return element.replace('NULL','')

def format_datetime_bq(element):
    from datetime import datetime as dt
    """This function takes a string with comma separated values as input and
    replaces a datetime value in the format with '%m/%d/%Y %H:%M' with a
    datetime value in the format '%Y-%m-%d %H:%M:%S'
    Example input string:
    '10000085,1526,7239,10/03/2020 13:28,Bloor St W / Manning Ave - SMART,7544,
    10/03/2020 13:53,Foster Pl / Elizabeth St - SMART,3956,Annual Member'
    Example output string:
    '10000083,720,7239,2020-10-03 13:28:00,Bloor St W / Manning Ave - SMART,7160,
    2020-10-03 13:40:00,King St W / Tecumseth St,5563,Annual Member'
    """
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
    """This method translates a single line of comma separated values to a dictionary 
    which can be loaded into BigQuery.
    Args:
    string_input: A comma separated list of values in the form: 'Trip_Id, Trip__Duration,
    Start_Station_Id, Start_Time, Start_Station_Name, End_Station_Id, End_Time, 
    End_Station_Name, Bike_Id, User_Type'
    Example string_input: '10000083,720,7239,2020-03-10 13:28:00,
    Bloor St W / Manning Ave - SMART,7160, 10/03/2020 13:40,
    King St W / Tecumseth St,5563,Annual Member'
    Returns:
    A dict mapping BigQuery column names as keys to the corresponding value
    parsed from string_input.
    Example output:
        {'Trip_Id':'10000083',
        'Trip__Duration':'720',
        'Start_Station_Id':'7239',
        'Start_Time':'2020-03-10 13:28:00',
        'Start_Station_Name':'Bloor St W / Manning Ave - SMART',
        'End_Station_Id':'7160',
        'End_Time':'2020-10-03 13:40:00',
        'End_Station_Name':'King St W / Tecumseth St',
        'Bike_Id':'5563',
        'User_Type':'Annual Member'}
    """
    # Strip out carriage return, newline and quote characters.
    values = re.split(",", re.sub('\r\n', '', re.sub('"', '',string_input)))
    row = dict(
        zip(('Trip_Id', 'Trip__Duration', 'Start_Station_Id', 'Start_Time',
        'Start_Station_Name', 'End_Station_Id', 'End_Time', 'End_Station_Name',
        'Bike_Id', 'User_Type'),values))
    return row


def run(argv=None):
    """The main function which creates the pipeline and runs it."""

    parser = argparse.ArgumentParser()

    # Here we add some specific command line arguments we expect.
    # Specifically we have the input file to read and the output table to write.
    # This is the final stage of the pipeline, where we define the destination
    # of the data. In this case we are writing to BigQuery.
    parser.add_argument(
        '--input',
        dest='input',
        required=False,
        help='Input file to read. This can be a local file or '
        'a file in a Google Storage Bucket.',
        default='gs://customer-demos-asia-south1/dataflow/input/*.csv')

    # This defaults to the bucket in your BigQuery project. You'll have
    # to create the bucket yourself using this command:
    # bq mk my-bucket
    parser.add_argument('--output',
                        dest='output',
                        required=False,
                        help='Output BQ table to write results to.',
                        default='dataflow_python.biketrips2020')

    # Parse arguments from the command line.
    known_args, pipeline_args = parser.parse_known_args(argv)

    # Initiate the pipeline using the pipeline arguments passed in from the
    # command line. This includes information such as the project ID and
    # where Dataflow should store temp files.
    p = beam.Pipeline(options=PipelineOptions(pipeline_args))

    (p
    # Read the file. This is the source of the pipeline. All further
    # processing starts with lines read from the file. We use the input
    # argument from the command line. We also skip the first line which is a
    # header row.
    | 'Read File' >> beam.io.ReadFromText(known_args.input, skip_header_lines=1)

    # This stage of the pipeline reads individual rows and transforms them
    # according to the logic defined in the functions
    | 'Deconcactenate Columns' >> beam.Map(deconcat)
    | 'Replace Nulls' >> beam.Map(replace_nulls)
    | 'Convert to BQ Datetime' >> beam.Map(format_datetime_bq)

    # This stage of the pipeline translates from a CSV file single row
    # input as a string, to a dictionary object consumable by BigQuery.
    # It refers to a function we have written. This function will
    # be run in parallel on different workers using input from the
    # previous stage of the pipeline.
    | 'String To BigQuery Row' >> beam.Map(parse_method)
    | 'Write To BigQuery' >> beam.io.Write(
    beam.io.WriteToBigQuery(
    # The table name is a required argument for the BigQuery sink.
    # In this case we use the value passed in from the command line.
    known_args.output,
    # Here we use the simplest way of defining a schema:
    # fieldName:fieldType
    schema='Trip_Id:INTEGER,Trip__Duration:INTEGER,Start_Station_Id:INTEGER,'
    'Start_Time:DATETIME,Start_Station_Name:STRING,End_Station_Id:INTEGER,'
    'End_Time:DATETIME, End_Station_Name:STRING, Bike_Id:INTEGER, User_Type:STRING',
    # Creates the table in BigQuery if it does not yet exist.
    create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
    # Deletes all data in the BigQuery table before writing.
    write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE)))
    p.run().wait_until_finish()

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.WARNING)
    run()
