import os
import shutil
import uuid
import cv2
import numpy as np
from fastapi import UploadFile
from src.core.config import PLANT_MODEL_PATH, VALORISATION_MODEL_PATH
from src.api.utils.model_loader import get_models

UPLOAD_DIR = "uploads/diagnostics"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def save_upload_file(upload_file: UploadFile, sub_dir: str = "diagnostics") -> str:
    """Sauvegarde l'image et retourne le chemin relatif."""
    target_dir = os.path.join(UPLOAD_DIR, sub_dir)
    os.makedirs(target_dir, exist_ok=True)
    
    file_extension = upload_file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
    file_path = os.path.join(target_dir, unique_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    
    return file_path

def run_prediction(image_path: str):
    """Exécute la prédiction YOLO pour les plantes."""
    models = get_models()
    model = models.get('plant')
    if not model:
        return "Inconnu", "Indéterminé", "Service IA indisponible", {}

    results = model(image_path)
    
    disease = "Sain"
    severity = "Faible"
    advice = "Aucun traitement nécessaire"
    detection_details = {"label": "Sain", "confidence": 1.0, "boxes": []}

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
        
        # Détails complets des boxes
        boxes = []
        for box in results[0].boxes:
            b_class_id = int(box.cls[0].item())
            boxes.append({
                "x_min": float(box.xyxy[0][0].item()),
                "y_min": float(box.xyxy[0][1].item()),
                "x_max": float(box.xyxy[0][2].item()),
                "y_max": float(box.xyxy[0][3].item()),
                "confidence": float(box.conf[0].item()),
                "label": results[0].names[b_class_id]
            })
        
        detection_details = {
            "label": disease,
            "confidence": confidence,
            "boxes": boxes
        }

    return disease, severity, advice, detection_details

def run_valorisation_prediction(image_path: str):
    """Exécute la prédiction YOLO pour le contrôle qualité (Valorisation)."""
    models = get_models()
    model = models.get('valorisation')
    if not model:
        return {}, 0.5, 0.0, "MECANIQUE", {}

    results = model(image_path)
    
    visual_defects = {}
    healthy_score = 1.0
    taux_defauts = 0.0
    decision = "DIRECT_EMBALLAGE"
    detection_details = {"label": "Sain", "confidence": 1.0, "boxes": []}

    if len(results) > 0 and len(results[0].boxes) > 0:
        total_items = len(results[0].boxes)
        defects_count = 0
        boxes = []
        
        for box in results[0].boxes:
            class_id = int(box.cls[0].item())
            label = results[0].names[class_id]
            conf = float(box.conf[0].item())
            
            boxes.append({
                "x_min": float(box.xyxy[0][0].item()),
                "y_min": float(box.xyxy[0][1].item()),
                "x_max": float(box.xyxy[0][2].item()),
                "y_max": float(box.xyxy[0][3].item()),
                "confidence": conf,
                "label": label
            })

            if label.lower() != "sain":
                defects_count += 1
                visual_defects[label] = visual_defects.get(label, 0) + 1
        
        taux_defauts = (defects_count / total_items) if total_items > 0 else 0
        healthy_score = 1.0 - taux_defauts
        
        # Décision automatique : si plus de 20% de défauts -> Tri mécanique
        if taux_defauts > 0.2:
            decision = "MECANIQUE"
        
        detection_details = {
            "label": "Mixed" if defects_count > 0 else "Sain",
            "confidence": 1.0 - taux_defauts,
            "boxes": boxes
        }

    return visual_defects, healthy_score, taux_defauts, decision, detection_details

async def analyze_frame(frame_bytes: bytes):
    """Inférence rapide sur une frame vidéo (bytes)."""
    nparr = np.frombuffer(frame_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    models = get_models()
    model = models.get('plant') # Utilise le modèle plante par défaut pour le streaming
    if not model:
        return {"label": "Service IA indisponible", "confidence": 0, "boxes": []}

    results = model(img)
    
    if len(results) > 0 and len(results[0].boxes) > 0:
        best_box = results[0].boxes[0]
        class_id = int(best_box.cls[0].item())
        
        boxes = []
        for box in results[0].boxes:
            b_class_id = int(box.cls[0].item())
            boxes.append({
                "x_min": float(box.xyxy[0][0].item()),
                "y_min": float(box.xyxy[0][1].item()),
                "x_max": float(box.xyxy[0][2].item()),
                "y_max": float(box.xyxy[0][3].item()),
                "confidence": float(box.conf[0].item()),
                "label": results[0].names[b_class_id]
            })

        return {
            "label": results[0].names[class_id],
            "confidence": float(best_box.conf[0].item()),
            "boxes": boxes
        }
    
    return {"label": "Sain", "confidence": 1.0, "boxes": []}
