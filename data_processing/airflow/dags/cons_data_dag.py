from airflow import DAG
from airflow.datasets import Dataset
from datetime import datetime
import os
import sys
from airflow.operators.python import PythonOperator

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
    


from tasks.kaggle_uploader import export_to_kaggle

with DAG(
    dag_id='export_consumer_dataset_to_kaggle',
    schedule_interval=None,  
    start_date=datetime(2026, 3, 1),
    catchup=False,
    tags=['ai', 'dataset', 'consumer'],
) as dag:

    
    upload_task = PythonOperator(
        task_id='upload_consumer_to_kaggle',
        python_callable=export_to_kaggle,
        op_kwargs={
            'local_dir': '/opt/airflow/data/raw/consumer/Fresh-Rotten 1.v4i.yolo26',
            'dataset_slug': 'fresh-rotten-1',
            'dataset_title': 'Fresh-Rotten 1 Dataset'
        })

    upload_task