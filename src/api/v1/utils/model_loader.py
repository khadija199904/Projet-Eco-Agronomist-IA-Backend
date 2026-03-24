from ultralytics import YOLO
from src.core.config import PLANT_MODEL_PATH, VALORISATION_MODEL_PATH,CONSUMER_MODEL_PATH

def get_models():
    """Charge les modèles YOLO."""
    models = {}
    
    try:
        models['plant'] = YOLO(PLANT_MODEL_PATH)
        models['valorisation'] = YOLO(VALORISATION_MODEL_PATH)
        models['consumer'] = YOLO(CONSUMER_MODEL_PATH)
        print("Modèles chargés avec succès.")
        print(models['plant'].info())
        
    except Exception as e:
        print(f"Erreur de chargement: {e}")
        
    return models
