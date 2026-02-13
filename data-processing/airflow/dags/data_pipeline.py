from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime
import os
import sys

# Ensure parent 'airflow' folder is on sys.path so we can import sibling 'tasks' package
current_dir = os.path.dirname(__file__)
airflow_dir = os.path.dirname(current_dir)
if airflow_dir not in sys.path:
    sys.path.insert(0, airflow_dir)

from tasks.bronze_ingestion import download_dataset
SILVER_SCRIPT = os.path.join(airflow_dir, "tasks", "tasks.silver_transformation ")


with DAG('medallion_agadir_plantdoc', start_date=datetime(2024, 1, 1), schedule=None,catchup=False) as dag:

    #  BRONZE : Ingestion brute
    ingest_task = PythonOperator(
        task_id='ingest_kaggle_to_bronze',
        python_callable=download_dataset
    )
    
    # SILVER : Filtrage des plantes d'Agadir (à implémenter)
    silver_task = SparkSubmitOperator(
        task_id='pyspark_silver_filtering',
        application=SILVER_SCRIPT,
        conn_id='spark_default'
    )
    
    
    ingest_task  >> silver_task 