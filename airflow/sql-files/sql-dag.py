# --------------------------------------------------------------------------------
# Load The Dependencies
# --------------------------------------------------------------------------------
from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.operators.email_operator import EmailOperator
from airflow.utils.dates import days_ago, timedelta,datetime
# --------------------------------------------------------------------------------
# Set default arguments
# --------------------------------------------------------------------------------
# If you are running Airflow in more than one time zone
# see https://airflow.apache.org/docs/apache-airflow/stable/timezone.html
# for best practices

default_args = {"owner": "RevisitClass",
                "start_date": datetime(2023, 1, 7),
                "email": "test@gmail.com",
                "email_on_failure": True,
                "email_on_retry": True,
                "retries": 3,
                "retry_delay": timedelta(minutes=5)}
# --------------------------------------------------------------------------------
# DAG
# --------------------------------------------------------------------------------
with DAG("daily_refresh_rc_bigquery",
         default_args=default_args,
         description="Run the sample Biqguery sql",
         schedule_interval="@daily",
         start_date=days_ago(2),
         catchup=False,
         template_searchpath="/home/airflow/gcs/dags/scripts"
         ) as dag:

        download_from_bb = {

        }

        run_base = BigQueryInsertJobOperator(
            task_id="compliance_base",
            configuration={"query": {"query": "{% include 'sample1.sql' %}",
                                     "useLegacySql": False}},
            location="asia-south1"
        )
           
        run_analytics = BigQueryInsertJobOperator(
            task_id="compliance_analytics",
            configuration={"query": {"query": "{% include 'sample2.sql' %}",
                                     "useLegacySql": False}},
            location="asia-south1"
        )

        run_base>>run_analytics
