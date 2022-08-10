import os
import datetime
from airflow import models
from airflow.providers.google.cloud.operators.dataproc import (
   DataprocCreateClusterOperator,
   DataprocSubmitJobOperator
)
from airflow.providers.google.cloud.sensors.dataproc import DataprocJobSensor
from airflow.utils.dates import days_ago

PROJECT_ID = models.Variable.get('project_id')
CLUSTER_NAME =  "spark-demo"
REGION = models.Variable.get('region')
ZONE = models.Variable.get('zone')
PYSPARK_URI = models.Variable.get('pyspark-demo-uri')

YESTERDAY = datetime.datetime.now() - datetime.timedelta(days=1)

default_dag_args = {
    'start_date': YESTERDAY,
}

# Cluster definition
# [START how_to_cloud_dataproc_create_cluster]

CLUSTER_CONFIG = {
   "master_config": {
       "num_instances": 1,
       "machine_type_uri": "n1-standard-4",
       "disk_config": {"boot_disk_type": "pd-standard", "boot_disk_size_gb": 1024},
   },
   "worker_config": {
       "num_instances": 2,
       "machine_type_uri": "n1-standard-4",
       "disk_config": {"boot_disk_type": "pd-standard", "boot_disk_size_gb": 1024},
   },
   "gce_cluster_config":{
        "subnetwork_uri":"https://www.googleapis.com/compute/v1/projects/on-prem-project-337210/regions/asia-south1/subnetworks/on-prem-subnet-mumbai"   
   }
}

with models.DAG(
   "dataproc-demo-pyspark",
   schedule_interval=datetime.timedelta(days=1),
   default_args=default_dag_args) as dag:

   # [START how_to_cloud_dataproc_create_cluster_operator]
   create_cluster = DataprocCreateClusterOperator(
       task_id="create_cluster",
       project_id=PROJECT_ID,
       cluster_config=CLUSTER_CONFIG,
       region=REGION,
       cluster_name=CLUSTER_NAME
   )

   PYSPARK_JOB = {
   "reference": {"project_id": PROJECT_ID},
   "placement": {"cluster_name": CLUSTER_NAME},
   "pyspark_job": {"main_python_file_uri": PYSPARK_URI},
   }

   pyspark_task = DataprocSubmitJobOperator(
       task_id="pyspark_task", job=PYSPARK_JOB, location=REGION, project_id=PROJECT_ID
   )

   delete_cluster = DataprocDeleteClusterOperator(
    task_id="delete_cluster",
    project_id=PROJECT_ID,
    cluster_name=CLUSTER_NAME,
    region=REGION,
   )

   create_cluster >>  pyspark_task >> delete_cluster
