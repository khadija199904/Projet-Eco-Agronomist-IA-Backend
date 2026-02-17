from airflow import DAG

from datetime import datetime
import os
import sys

# Ensure parent 'airflow' folder is on sys.path so we can import sibling 'tasks' package
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)



from tasks.bronze_ingestion import download_dataset
from tasks.kaggle_uploader import upload_to_kaggle

from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

SILVER_SCRIPT = os.path.join(ROOT_DIR, "tasks", "silver.py")



with DAG('medallion_plantdoc', start_date=datetime(2024, 1, 1), schedule=None,catchup=False) as dag:

    #  BRONZE : Ingestion brute
    ingest_task = PythonOperator(
        task_id='ingest_kaggle_to_bronze',
        python_callable=download_dataset
    )
    
    # SILVER : Filtrage des plantes d'Agadir (à implémenter)
    silver_task = SparkSubmitOperator(
    task_id='pyspark_silver_filtering',
    conn_id='spark_default',
    application='/opt/airflow/tasks/silver.py'
)
        
    
    #  UPLOAD KAGGLE
    upload_task = PythonOperator(
        task_id='upload_result_to_kaggle',
        python_callable=upload_to_kaggle
    )

    # Enchaînement des tâches
    ingest_task >> silver_task >> upload_task
    
    