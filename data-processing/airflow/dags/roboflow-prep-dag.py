from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime
from tasks.prod_data_roboflow import standardize_roboflow

with DAG('roboflow_standardization_pipeline', 
         start_date=datetime(2026, 2, 17), 
         schedule_interval=None) as dag:

    
    t1 = PythonOperator(
        task_id='standardize_roboflow_files',
        python_callable=standardize_roboflow
    )

    # Déclencher le DAG principal automatiquement après
    t2 = TriggerDagRunOperator(
        task_id='trigger_main_pipeline',
        trigger_dag_id='medallion_plant_disease_v1' ,
        wait_for_completion=True,  
        poke_interval=30,          
        deferrable=True
    )

    t1 >> t2