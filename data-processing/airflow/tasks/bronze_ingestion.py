import os
from dotenv import load_dotenv
import shutil
from kaggle.api.kaggle_api_extended import KaggleApi

def download_dataset():
    load_dotenv()
    
    # Set environment variables from .env or kaggle.json
    os.environ['KAGGLE_USERNAME'] = os.getenv('KAGGLE_USERNAME')
    os.environ['KAGGLE_KEY'] = os.getenv('KAGGLE_KEY')
    
    api = KaggleApi()
    api.authenticate()
    print("Authentification réussie !")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    bronze_path = os.path.join(base_dir, "../data/bronze/plant-doc")
    dataset_id = "yusufmurtaza01/plantdoc-object-detection-dataset"

 

    # Téléchargement et Décompression
    print(f"Téléchargement du dataset {dataset_id} en cours...")
    
    api.dataset_download_files(dataset_id, path=bronze_path, unzip=True)
    

if __name__ == "__main__":
    download_dataset ()