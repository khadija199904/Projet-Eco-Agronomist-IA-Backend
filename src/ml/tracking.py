import os
import mlflow
def setup_mlflow():
    """Sets up MLflow to use a local database instead of the deprecated filesystem backend."""
    # Use a local SQLite database
    tracking_uri = "sqlite:///mlflow.db"
    mlflow.set_tracking_uri(tracking_uri)
    
    # Create or set the experiment
    experiment_name = "AgriVision_Training"
    if not mlflow.get_experiment_by_name(experiment_name):
        mlflow.create_experiment(experiment_name)
    mlflow.set_experiment(experiment_name)
    
    # Important: Tell Ultralytics to use this URI
    os.environ["MLFLOW_TRACKING_URI"] = tracking_uri
    os.environ["MLFLOW_EXPERIMENT_NAME"] = experiment_name