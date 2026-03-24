import os
import shutil
from kaggle.api.kaggle_api_extended import KaggleApi

def ingest_dataset():

    
    api = KaggleApi()
    try:
        api.authenticate()
        print("Authentification réussie via Docker Env !")
    except Exception as e:
        print(f"Erreur : Vérifiez que KAGGLE_USERNAME et KAGGLE_KEY sont bien dans Docker. {e}")
        raise
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    bronze_path = os.path.join(base_dir, "../data/bronze/plant-doc")
    dataset_id = "yusufmurtaza01/plantdoc-object-detection-dataset"

    # Téléchargement et Décompression
    print(f"Téléchargement du dataset {dataset_id} en cours...")
    
    api.dataset_download_files(dataset_id, path=bronze_path, unzip=True)

    print(f"Ingestion depuis kaggle terminée")
     
     #---------------Roboflow-------------------------
    RAW_ROBO = "/opt/airflow/data/raw/roboflow_standardized"
    BRONZE_ROBO = "/opt/airflow/data/bronze/roboflow"
    
    print("--- Ingestion Bronze : Transfert Roboflow ---")

    if not os.path.exists(RAW_ROBO):
        print(f"Erreur : Source {RAW_ROBO} introuvable.")
        return

    # Nettoyage et copie vers Bronze
    if os.path.exists(BRONZE_ROBO):
        shutil.rmtree(BRONZE_ROBO)
    
    shutil.copytree(RAW_ROBO, BRONZE_ROBO)
    print(f"Données Roboflow copiées avec succès vers {BRONZE_ROBO}")
    print(f"Ingestion Bronze Totale terminée.")


if __name__ == "__main__":
    ingest_dataset ()