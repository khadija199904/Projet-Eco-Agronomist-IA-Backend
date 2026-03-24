from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from tasks.kaggle_uploader import export_to_kaggle # noqa: E402
from tasks.silver_valor import valorisation_fusion # noqa: E402

with DAG(
    'data_valorisation_pipeline',
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=['valorisation', 'fusion']
) as dag:

    valorisation_task = PythonOperator(
        task_id='fusion_and_filter_valorisation',
        python_callable=valorisation_fusion
    )
    upload_kaggle_task = PythonOperator(
        task_id='upload_anomalies_to_kaggle',
        python_callable=export_to_kaggle,
        op_kwargs={
            'local_dir': '/opt/airflow/data/silver/fruits-vegetables-disease-detection',
            'dataset_slug': 'fruits-vegetables-disease-detection',
            'dataset_title': 'Fruits Vegetables Disease Detection Dataset'
        }
    )

    valorisation_task >> upload_kaggle_task
