import os
import shutil
import uuid
import cv2
import numpy as np
import io
from PIL import Image
from fastapi import UploadFile
from src.core.config import PLANT_MODEL_PATH, VALORISATION_MODEL_PATH
from src.api.utils.model_loader import get_models


SHORT_NAMES_MAP = {
    "Corn leaf blight": "Corn_Blight",
    "Corn rust leaf": "Corn_Rust",
    "Tomato leaf late blight": "Tom_Late_Blight",
    "Tomato mold leaf": "Tom_Mold",
    "Tomato leaf yellow virus": "Tom_Yellow_Virus",
    "Tomato leaf mosaic virus": "Tom_Mosaic",
    "Tomato leaf bacterial spot": "Tom_Bacterial",
    "Squash Powdery mildew leaf": "Squash_Powdery",
    "Corn Gray leaf spot": "Corn_Gray_Spot",
    "Tomato Early blight leaf": "Tom_Early_Blight",
    "Tomato Septoria leaf spot": "Tom_Septoria",
    "Bell_pepper leaf spot": "Pepper_Spot",
    "Tomato two spotted spider mites leaf": "Tom_Mites",
    "Nutrient Deficiencies": "Nutrient_Def",
    "White bugs": "White_Bugs",
    "Tomato leaf": "Tomato_Health",
    "Bell_pepper leaf": "Pepper_Health",
    "Blueberry leaf": "Blueberry_Health"
}

def run_prediction(image_data: bytes):
    """Exécute la prédiction YOLO pour les plantes directement depuis le fichier en mémoire."""
    models = get_models()
    model = models.get('plant')
    if not model:
        return "Inconnu", None, {"label": "Service IA indisponible", "confidence": 0, "has_boxes": False}
    
    image = Image.open(io.BytesIO(image_data)).convert("RGB")
    results = model(image, conf=0.25)
    
    disease = "Sain"
    # Temporarire pour les conseils (à remplacer par un RAG) 
    advices_map = {"Tomato Septoria leaf spot": "Utilisez un fongicide à base de cuivre et retirez les feuilles infectées."}
    advice = advices_map.get(disease, "Surveillez l'évolution de la plante.")
    
    detections = []
    image_path = None

    if len(results) > 0 and len(results[0].boxes) > 0:
        result = results[0]
        original_names = result.names.copy()
        short_names = {
            id: SHORT_NAMES_MAP.get(name, name) 
            for id, name in original_names.items()
        }
        result.names = short_names
        im_array = result.plot()

        result.names = original_names
        # 2. Extraire TOUTES les détections pour le dictionnaire
        for box in result.boxes:
            class_id = int(box.cls[0])
            detections.append({
                "bbox": [round(x, 1) for x in box.xyxy[0].tolist()],
                "conf": round(float(box.conf[0]), 2),
                "class": class_id,
                "name": original_names[class_id] # Nom complet ici
            })

        # 3. Identifier la maladie principale (la plus probable)
        best_box = result.boxes[0]
        disease = original_names[int(best_box.cls[0])]
        max_confidence = float(best_box.conf[0])

       
        # Sauvegarde de l'image (avec les noms courts déjà dessinés)
        target_dir = os.path.join("uploads", "diagnostics")
        os.makedirs(target_dir, exist_ok=True)
        unique_filename = f"{uuid.uuid4().hex}.jpg"
        image_path = os.path.join(target_dir, unique_filename)
        
        
        cv2.imwrite(image_path, im_array)

        # 5. Préparer les détails finaux
        detection_details = {
            "label": disease,
            "confidence": round(max_confidence, 2),
            "image_url": image_path,
            "all_detections": detections  #
        }
    else:
        
        detection_details = {
            "label": "Sain",
            "confidence": 1.0,
            "all_detections": []
        }

    return disease, advice, detection_details

# def run_valorisation_prediction(image_path: str):
#     """Exécute la prédiction YOLO pour le contrôle qualité (Valorisation)."""
#     models = get_models()
#     model = models.get('valorisation')
#     if not model:
#         return {}, 0.5, 0.0, "MECANIQUE", {}

#     results = model(image_path)
    
#     visual_defects = {}
#     healthy_score = 1.0
#     taux_defauts = 0.0
#     decision = "DIRECT_EMBALLAGE"
#     detection_details = {"label": "Sain", "confidence": 1.0, "boxes": []}

#     if len(results) > 0 and len(results[0].boxes) > 0:
#         total_items = len(results[0].boxes)
#         defects_count = 0
#         boxes = []
        
#         for box in results[0].boxes:
#             class_id = int(box.cls[0].item())
#             label = results[0].names[class_id]
#             conf = float(box.conf[0].item())
            
#             boxes.append({
#                 "x_min": float(box.xyxy[0][0].item()),
#                 "y_min": float(box.xyxy[0][1].item()),
#                 "x_max": float(box.xyxy[0][2].item()),
#                 "y_max": float(box.xyxy[0][3].item()),
#                 "confidence": conf,
#                 "label": label
#             })

#             if label.lower() != "sain":
#                 defects_count += 1
#                 visual_defects[label] = visual_defects.get(label, 0) + 1
        
#         taux_defauts = (defects_count / total_items) if total_items > 0 else 0
#         healthy_score = 1.0 - taux_defauts
        
#         # Décision automatique : si plus de 20% de défauts -> Tri mécanique
#         if taux_defauts > 0.2:
#             decision = "MECANIQUE"
        
#         detection_details = {
#             "label": "Mixed" if defects_count > 0 else "Sain",
#             "confidence": 1.0 - taux_defauts,
#             "boxes": boxes
#         }

#     return visual_defects, healthy_score, taux_defauts, decision, detection_details

# async def analyze_frame(frame_bytes: bytes):
#     """Inférence rapide sur une frame vidéo (bytes)."""
#     nparr = np.frombuffer(frame_bytes, np.uint8)
#     img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
#     models = get_models()
#     model = models.get('plant') # Utilise le modèle plante par défaut pour le streaming
#     if not model:
#         return {"label": "Service IA indisponible", "confidence": 0, "boxes": []}

#     results = model(img)
    
#     if len(results) > 0 and len(results[0].boxes) > 0:
#         best_box = results[0].boxes[0]
#         class_id = int(best_box.cls[0].item())
        
#         boxes = []
#         for box in results[0].boxes:
#             b_class_id = int(box.cls[0].item())
#             boxes.append({
#                 "x_min": float(box.xyxy[0][0].item()),
#                 "y_min": float(box.xyxy[0][1].item()),
#                 "x_max": float(box.xyxy[0][2].item()),
#                 "y_max": float(box.xyxy[0][3].item()),
#                 "confidence": float(box.conf[0].item()),
#                 "label": results[0].names[b_class_id]
#             })

#         return {
#             "label": results[0].names[class_id],
#             "confidence": float(best_box.conf[0].item()),
#             "boxes": boxes
#         }
    
#     return {"label": "Sain", "confidence": 1.0, "boxes": []}
