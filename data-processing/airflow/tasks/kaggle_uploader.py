import os
import json
from dotenv import load_dotenv
from kaggle.api.kaggle_api_extended import KaggleApi

def upload_to_kaggle():
    load_dotenv() 
    
    api = KaggleApi()
    api.authenticate()
    
    silver_path = "data/silver/plant_dataset_DetectionObject"
    username = api.get_config_value('username')
    dataset_slug = "plant-dataset-yolo"

    meta = {
        "title": "Agadir Dataset YOLO",
        "id": f"{username}/{dataset_slug}",
        "licenses": [{"name": "CC0-1.0"}]
    }
    
    with open(os.path.join(silver_path, "dataset-metadata.json"), "w") as f:
        json.dump(meta, f)
    
    print("Envoi en cours vers Kaggle...")
    api.dataset_create_new(silver_path, dir_mode='zip')
    print(f"Succès ! Dataset : kaggle.com/datasets/{username}/{dataset_slug}")

if __name__ == "__main__":
    upload_to_kaggle()