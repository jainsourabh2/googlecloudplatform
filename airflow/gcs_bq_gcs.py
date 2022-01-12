# --------------------------------------------------------------------------------
# Load The Dependencies
# --------------------------------------------------------------------------------

import csv
import datetime
import io
import logging
import os

from airflow import models
from airflow.operators import dummy
from airflow.providers.google.cloud.transfers import gcs_to_bigquery
from airflow.providers.google.cloud.transfers import gcs_to_gcs
from airflow.operators.python import BranchPythonOperator
from airflow.utils.trigger_rule import TriggerRule

# --------------------------------------------------------------------------------
# Set default arguments
# --------------------------------------------------------------------------------

# If you are running Airflow in more than one time zone
# see https://airflow.apache.org/docs/apache-airflow/stable/timezone.html
# for best practices
yesterday = datetime.datetime.now() - datetime.timedelta(days=1)

default_args = {
    'owner': 'airflow',
    'start_date': datetime.datetime.now(),
    'depends_on_past': False,
    'email': [''],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': datetime.timedelta(minutes=5),
}

# --------------------------------------------------------------------------------
# Set variables
# --------------------------------------------------------------------------------

# Source Bucket
source_bucket = models.Variable.get('gcs_source_bucket')

# Interim Bucket
interim_bucket = models.Variable.get('gcs_interim_bucket')

# Archival Bucket
dest_bucket = models.Variable.get('gcs_archival_bucket')

# --------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------


def gcs_file_count():
    """
    Count the files in the GCS Object path
    """
    result = os.popen('gsutil ls gs://'+interim_bucket+'/ | wc -l')
    output = result.read()
    #output = 1
    if int(output) > 0:
        return 'GCS_to_BQ'
    else:
        return 'end_no_files'

# --------------------------------------------------------------------------------
# Main DAG
# --------------------------------------------------------------------------------

# Define a DAG (directed acyclic graph) of tasks.
# Any task you create within the context manager is automatically added to the
# DAG object.
with models.DAG(
        'cloud_composer_gcs_to_bq_final',
        default_args=default_args,
        schedule_interval=datetime.timedelta(minutes=15)) as dag:
    
    start = dummy.DummyOperator(
        task_id='start',
        trigger_rule='all_success'
    )

    GCS_to_GCS = gcs_to_gcs.GCSToGCSOperator(
        # Replace ":" with valid character for Airflow task
        task_id='GCS_to_GCS_Move_Files_From_Source_To_Interim_Bucket',
        source_bucket=source_bucket,
        source_object='*.csv',
        destination_bucket=interim_bucket,
        move_object=True
    )
    
    GCS_File_Count = BranchPythonOperator(
        task_id='gcs_file_count',
        python_callable=gcs_file_count,
        do_xcom_push=False
    )

    GCS_to_BQ = gcs_to_bigquery.GCSToBigQueryOperator(
        # Replace ":" with valid character for Airflow task
        task_id='GCS_to_BQ',
        bucket=interim_bucket,
        source_objects=['*.csv'],
        destination_project_dataset_table='sourabhjainceanalytics.demo.users',
        source_format='CSV',
        write_disposition='WRITE_TRUNCATE',
        create_disposition='CREATE_NEVER',
        skip_leading_rows=1
    )

    GCS_to_GCS_Archive = gcs_to_gcs.GCSToGCSOperator(
        # Replace ":" with valid character for Airflow task
        task_id='_GCS_to_GCS_Move_Files_From_Interim_To_Destination_Bucket',
        source_bucket=interim_bucket,
        source_object='*.csv',
        destination_bucket=dest_bucket,
        move_object=True
    )    
    
    end_no_files = dummy.DummyOperator(
        task_id='end_no_files',
        trigger_rule='all_success'
    )

    end = dummy.DummyOperator(
        task_id='end',
        trigger_rule='all_success'
    )

    start >> GCS_to_GCS >> GCS_File_Count >> GCS_to_BQ >> GCS_to_GCS_Archive >> end
    start >> GCS_to_GCS >> GCS_File_Count >> end_no_files