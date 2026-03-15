
import os
import json
import logging
from kaggle.api.kaggle_api_extended import KaggleApi

def export_to_kaggle(local_dir, dataset_slug, dataset_title, version_notes="Update via Airflow"):
    """
    Exporte un dossier local vers Kaggle. 
    Gère la création initiale et la mise à jour des versions.
    """
    # Configuration du logger pour Airflow
    logger = logging.getLogger("airflow.task")
    
    api = KaggleApi()
    
    try:
        logger.info(f"Authentification Kaggle pour le dataset: {dataset_title}")
        api.authenticate()
        
        user_name = api.config_values.get('username')
        if not user_name:
            raise ValueError("Erreur: Username Kaggle introuvable. Vérifiez votre fichier kaggle.json")
            
        dataset_id = f"{user_name}/{dataset_slug}"
        
        
        metadata = {
            "title": dataset_title,
            "id": dataset_id,
            "licenses": [{"name": "CC0-1.0"}]
        }
        
        metadata_path = os.path.join(local_dir, 'dataset-metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=4)
        
        logger.info(f"Metadata généré dans {metadata_path}")

        
        datasets = api.dataset_list(user=user_name, search=dataset_slug)
        exists = any(d.ref == dataset_id for d in datasets)

        if not exists:
            logger.info(f"Le dataset n'existe pas. Création en cours : {dataset_id}")
            
            api.dataset_create_new(folder=local_dir, dir_mode='zip')
        else:
            logger.info(f"Le dataset existe. Envoi d'une nouvelle version : {dataset_id}")
            
            api.dataset_create_version(
                folder=local_dir, 
                version_notes=version_notes,
                dir_mode='zip'
            )
            
        logger.info(f"--- SUCCESS: {dataset_title} est en ligne ! ---")

    except Exception as e:
        logger.error(f"--- FAILED: Export impossible ---")
        logger.error(f"Détails de l'erreur : {str(e)}")
        raise e

if __name__ == "__main__":
    pass