import os
import shutil
import uuid
import cv2
import numpy as np
import io
from PIL import Image
from fastapi import UploadFile
from src.core.config import PLANT_MODEL_PATH, VALORISATION_MODEL_PATH
from src.api.v1.utils.model_loader import get_models
from src.api.v1.utils.save_diagnostic import save_diagnostic_image



TARGETS = [
    {"en": "Corn leaf blight", "fr": "Helminthosporiose"},
    {"en": "Corn rust leaf", "fr": "Rouille"},
    {"en": "Tomato leaf late blight", "fr": "Mildiou"},
    {"en": "Tomato mold leaf", "fr": "Cladosporiose"},
    {"en": "Tomato leaf yellow virus", "fr": "Virus"},
    {"en": "Blueberry leaf", "fr": "Septoriose"},
    {"en": "Tomato leaf mosaic virus", "fr": "Mosaïque"},
    {"en": "Tomato leaf bacterial spot", "fr": "Gale bactérienne"},
    {"en": "Squash Powdery mildew leaf", "fr": "Oïdium"},
    {"en": "Corn Gray leaf spot", "fr": "Cercosporiose"},
    {"en": "Tomato Early blight leaf", "fr": "Alternariose"},
    {"en": "Tomato Septoria leaf spot", "fr": "Septoriose"},
    {"en": "Tomato leaf", "fr": "Tomate"}, 
    {"en": "Bell_pepper leaf spot", "fr": "Cercosporiose"},
    {"en": "Bell_pepper leaf", "fr": "Poivron"},
    {"en": "Tomato two spotted spider mites leaf", "fr": "Acariens"},
    {"en": "Nutrient Deficiencies", "fr": "Carence"},
    {"en": "White bugs", "fr": "Aleurodes"}
]

# Mapping rapide pour le code : { "English Name": "French Name" }
TRANSLATION_MAP = {t["en"]: t["fr"] for t in TARGETS}

CROP_MAP = {
    "Corn": "Maïs",
    "Tomato": "Tomate",
    "Blueberry": "Myrtille",
    "Squash": "Courge",
    "Bell_pepper": "Poivron"
}

def run_plant_prediction(image_data: bytes):
    """Exécute la prédiction YOLO pour les plantes directement depuis le fichier en mémoire."""
    models = get_models()
    model = models.get('plant')
    if not model:
        return "Inconnu", None, {"label": "Service IA indisponible"},[]
    
    image = Image.open(io.BytesIO(image_data)).convert("RGB")
    results = model(image, conf=0.25)
    
    if not results or len(results[0].boxes) == 0:
        return "Sain", {"label": "Sain", "confidence": 1.0, "all_detections": []}, []

    result = results[0]
    original_names = result.names.copy()
    
    # 1. Préparer les noms courts (Français) pour le plot()
    short_names_fr = {id: TRANSLATION_MAP.get(name, name) for id, name in original_names.items()}
    result.names = short_names_fr
    im_array = result.plot() 
    result.names = original_names

    # --- Extraction des Pathologies Uniques (pour le RAG) ---
    exclude = ["Tomato leaf", "Bell_pepper leaf", "Blueberry leaf"]
    detected_ids = set(int(box.cls[0]) for box in result.boxes)
    pathologies_fr = [
        TRANSLATION_MAP.get(original_names[i]) 
        for i in detected_ids 
        if original_names[i] not in exclude
    ]

    # --- Préparation des métadonnées ---
    best_box = result.boxes[0]
    eng_name = original_names[int(best_box.cls[0])]
    disease_fr = TRANSLATION_MAP.get(eng_name, "Inconnu")
    
    # Extraction de la culture
    crop_name = "Inconnu"
    for eng_prefix, fr_crop in CROP_MAP.items():
        if eng_name.startswith(eng_prefix):
            crop_name = fr_crop
            break

    # Sauvegarde physique
    image_path = save_diagnostic_image(im_array)

    detection_details = {
        "label": disease_fr,
        "culture": crop_name,
        "confidence": round(float(best_box.conf[0]), 2),
        "pathologies": pathologies_fr,
        "boxes": [
            {
                "coords": [round(x, 1) for x in box.xyxy[0].tolist()],
                "label": TRANSLATION_MAP.get(original_names[int(box.cls[0])])
            } for box in result.boxes
        ]
    }
    print("image_path",image_path)
    return disease_fr, detection_details, pathologies_fr ,image_path

async def get_rag_ordonnance(pathologies: list, culture: str = None):
    """
    Récupère les recommandations RAG en incluant la culture pour plus de précision.
    """
    from src.api.v1.services import rag_service
    return await rag_service.generate_plant_advice(pathologies, culture)

def run_valorisation_prediction(image_data: bytes):
    """Exécute la prédiction YOLO pour le contrôle qualité (Valorisation)."""
    models = get_models()
    model = models.get('valorisation')
    if not model:
        return {}, 0.5, 0.0, "MECANIQUE", {}, None

    # Chargement de l'image
    image = Image.open(io.BytesIO(image_data)).convert("RGB")
    results = model(image, conf=0.25)
    
    visual_defects = {}
    healthy_score = 1.0
    taux_defauts = 0.0
    decision = "DIRECT_EMBALLAGE"
    detection_details = {"label": "Sain", "confidence": 1.0, "boxes": []}
    image_path = None

    if len(results) > 0 and len(results[0].boxes) > 0:
        result = results[0]
        total_items = len(result.boxes)
        defects_count = 0
        boxes = []
        
        # 1. Générer l'image annotée (Plot)
        im_array = result.plot()
        image_path = save_diagnostic_image(im_array)

        for box in result.boxes:
            class_id = int(box.cls[0].item())
            label = result.names[class_id]
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
            "confidence": round(float(1.0 - taux_defauts), 2),
            "boxes": boxes
        }

    return visual_defects, healthy_score, taux_defauts, decision, detection_details, image_path

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
