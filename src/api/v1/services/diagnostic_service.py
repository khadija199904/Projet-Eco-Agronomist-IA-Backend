import os
import shutil
import uuid
from ultralytics import YOLO
from fastapi import UploadFile
from src.core.config import PLANT_MODEL_PATH
from src.api.v1.schemas.diagnostic_schema import PlantDiagnosticCreate

UPLOAD_DIR = "uploads/diagnostics"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class DiagnosticService:
    def __init__(self):
        self.model = self._load_model()

    def _load_model(self):
        try:
            if os.path.exists(PLANT_MODEL_PATH):
                return YOLO(PLANT_MODEL_PATH)
            else:
                print(f"AVERTISSEMENT: Modèle non trouvé au chemin : {PLANT_MODEL_PATH}")
                return None
        except Exception as e:
            print(f"Erreur lors du chargement du modèle YOLO: {e}")
            return None

    async def save_upload_file(self, upload_file: UploadFile) -> str:
        """Sauvegarde l'image et retourne le chemin relatif."""
        file_extension = upload_file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        
        return file_path

    def run_prediction(self, image_path: str):
        """Exécute la prédiction YOLO et retourne les résultats formatés."""
        if not self.model:
            return "Inconnu", "Indéterminé", "Service IA indisponible"

        results = self.model(image_path)
        
        disease = "Sain"
        severity = "Faible"
        advice = "Aucun traitement nécessaire"

        if len(results) > 0 and len(results[0].boxes) > 0:
            # Récupérer la détection la plus fiable
            best_box = results[0].boxes[0]
            class_id = int(best_box.cls[0].item())
            disease = results[0].names[class_id]
            confidence = float(best_box.conf[0].item())

            # Calculer la sévérité
            if confidence > 0.8: severity = "Haute"
            elif confidence > 0.5: severity = "Moyenne"

            # Recommandations (mapping simple)
            advices_map = {
                "mildiou": "Appliquer un fongicide à base de cuivre",
                "oidium": "Appliquer du soufre ou un produit systémique",
                "rouille": "Retirer les feuilles infectées et appliquer un traitement",
                "sain": "Plante en bonne santé. Continuer la surveillance"
            }
            advice = advices_map.get(disease.lower(), f"Analyse requise pour {disease}")

        return disease, severity, advice

# Instance unique du service (Singleton-like)
diagnostic_service = DiagnosticService()
