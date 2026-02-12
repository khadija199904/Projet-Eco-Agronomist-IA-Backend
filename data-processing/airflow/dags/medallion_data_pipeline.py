from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from scripts.bronze_ingestion import download_dataset # Import du script ci-dessus

with DAG('medallion_agadir_plantdoc', start_date=datetime(2024, 1, 1), schedule_interval=None) as dag:

    # STEP BRONZE : Ingestion brute
    ingest_task = PythonOperator(
        task_id='ingest_kaggle_to_bronze',
        python_callable=download_dataset
    )

    # STEP SILVER : PySpark filtrage (votre script silver.py)
    # silver_task = SparkSubmitOperator(...)

    ingest_task # >> silver_task