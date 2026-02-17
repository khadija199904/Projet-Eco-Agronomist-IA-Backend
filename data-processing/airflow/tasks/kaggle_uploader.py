import os
import json
from kaggle.api.kaggle_api_extended import KaggleApi

def export_to_kaggle():
    # 1. Configuration initiale
    SILVER_DIR = "/opt/airflow/data/silver"
    DATASET_SLUG = "agrivision-unified-plant-disease-18-classes"
    DATASET_TITLE = "AgriVision: Unified Plant Disease Dataset (18 Classes)"
    
   
    api = KaggleApi()
    
    try:
       
        print("Authentification à l'API Kaggle...")
        api.authenticate()
        
        user_name = api.config_values.get('username')
        if not user_name:
            raise ValueError("Username introuvable dans la config Kaggle.")
            
        dataset_id = f"{user_name}/{DATASET_SLUG}"
        print(f"Connecté en tant que : {user_name}")

        metadata = {
            "title": DATASET_TITLE,
            "id": dataset_id,
            "licenses": [{"name": "CC0-1.0"}]
        }
        
        with open(os.path.join(SILVER_DIR, 'dataset-metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=4)

        datasets = api.dataset_list(user=user_name, search=DATASET_SLUG)
        exists = any(d.ref == dataset_id for d in datasets)

        if not exists:
            print(f"Création d'un nouveau dataset : {dataset_id}")
            api.dataset_create_new(folder=SILVER_DIR, dir_mode='zip')
        else:
            print(f"Mise à jour du dataset : {dataset_id}")
            api.dataset_create_version(
                folder=SILVER_DIR, 
                version_notes="Update via Airflow: 18 classes re-indexed (PlantDoc + Roboflow)",
                dir_mode='zip'
            )
            
        print("--- Export Kaggle réussi ! ---")

    except Exception as e:
        print(f"--- ÉCHEC DE L'EXPORT ---")
        print(f"Erreur : {str(e)}")
        raise e

if __name__ == "__main__":
    export_to_kaggle()