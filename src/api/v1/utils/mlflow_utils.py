import mlflow
from src.core.config import MLFLOW_TRACKING_URI, MLFLOW_EXPERIMENT_NAME


def track_diagnostic(run_name: str, model_type: str, model_path: str, metrics: dict, params: dict, image_path: str = None):
    """
    Fonction utilitaire pour tracker un diagnostic dans MLflow.
    """
    try:
     
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)
        
        with mlflow.start_run(run_name=run_name):
            mlflow.log_param("model_type", model_type)
            mlflow.log_param("model_path", model_path)
            
            
            for key, value in params.items():
                mlflow.log_param(key, value)
            
            
            for key, value in metrics.items():
                mlflow.log_metric(key, value)
            
            if image_path:
                mlflow.log_artifact(image_path, "annotated_images")
    except Exception as e:
        print(f"Erreur tracking MLflow ({run_name}) : {e}")
