import os
from ultralytics import YOLO
from src.core.config import PLANT_MODEL_PATH, VALORISATION_MODEL_PATH

_models = {}

def get_models():
    """Charge et met en cache les modèles YOLO (Singleton)."""
    global _models
    if not _models:
        try:
            if os.path.exists(PLANT_MODEL_PATH):
                _models['plant'] = YOLO(PLANT_MODEL_PATH)
            
            if os.path.exists(VALORISATION_MODEL_PATH):
                _models['valorisation'] = YOLO(VALORISATION_MODEL_PATH)
            elif 'plant' in _models:
                # Utiliser le modèle plant par défaut si celui de valorisation manque
                _models['valorisation'] = _models['plant']
                
            print(f"Modèles YOLO chargés : {list(_models.keys())}")
        except Exception as e:
            print(f"Erreur lors du chargement des modèles YOLO: {e}")
    return _models
