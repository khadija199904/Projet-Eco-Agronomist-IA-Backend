import os
import shutil
import uuid
from ultralytics import YOLO
from fastapi import UploadFile
from src.core.config import PLANT_MODEL_PATH, VALORISATION_MODEL_PATH
from src.api.v1.schemas.diagnostic_schema import PlantDiagnosticCreate

UPLOAD_DIR = "uploads/diagnostics"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class DiagnosticService:
    def __init__(self):
        self.model = self._load_model()

    def _load_model(self):
        try:
            models = {}
            if os.path.exists(PLANT_MODEL_PATH):
                models['plant'] = YOLO(PLANT_MODEL_PATH)
            
            if os.path.exists(VALORISATION_MODEL_PATH):
                models['valorisation'] = YOLO(VALORISATION_MODEL_PATH)
            elif 'plant' in models:
                # Utiliser le modèle plant par défaut si celui de valorisation manque
                models['valorisation'] = models['plant']
                
            return models
        except Exception as e:
            print(f"Erreur lors du chargement des modèles YOLO: {e}")
            return {}

    async def save_upload_file(self, upload_file: UploadFile, sub_dir: str = "diagnostics") -> str:
        """Sauvegarde l'image et retourne le chemin relatif."""
        target_dir = os.path.join(UPLOAD_DIR, sub_dir)
        os.makedirs(target_dir, exist_ok=True)
        
        file_extension = upload_file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        file_path = os.path.join(target_dir, unique_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        
        return file_path

    def run_prediction(self, image_path: str):
        """Exécute la prédiction YOLO pour les plantes."""
        model = self.model.get('plant')
        if not model:
            return "Inconnu", "Indéterminé", "Service IA indisponible"

        results = model(image_path)
        
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

    def run_valorisation_prediction(self, image_path: str):
        """Exécute la prédiction YOLO pour le contrôle qualité (Valorisation)."""
        model = self.model.get('valorisation')
        if not model:
            return {}, 0.5, 0.0, "MECANIQUE"

        results = model(image_path)
        
        visual_defects = {}
        healthy_score = 1.0
        taux_defauts = 0.0
        decision = "DIRECT_EMBALLAGE"

        if len(results) > 0 and len(results[0].boxes) > 0:
            total_items = len(results[0].boxes)
            defects_count = 0
            
            for box in results[0].boxes:
                class_id = int(box.cls[0].item())
                label = results[0].names[class_id]
                conf = float(box.conf[0].item())
                
                if label.lower() != "sain":
                    defects_count += 1
                    visual_defects[label] = visual_defects.get(label, 0) + 1
            
            taux_defauts = (defects_count / total_items) if total_items > 0 else 0
            healthy_score = 1.0 - taux_defauts
            
            # Décision automatique : si plus de 20% de défauts -> Tri mécanique
            if taux_defauts > 0.2:
                decision = "MECANIQUE"

        return visual_defects, healthy_score, taux_defauts, decision

# Instance unique du service (Singleton-like)
diagnostic_service = DiagnosticService()
