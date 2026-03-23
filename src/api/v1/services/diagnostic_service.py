import os
import cv2
import numpy as np
from src.core.mapping import TRANSLATION_MAP, SHORT_CODE_MAP, CROP_MAP
from src.core.config import PLANT_MODEL_PATH, VALORISATION_MODEL_PATH , CONSUMER_MODEL_PATH
from src.api.v1.utils.model_loader import get_models
from src.api.v1.utils.save_diagnostic import save_diagnostic_image
from src.api.v1.utils.mlflow_utils import track_diagnostic

MODELS = get_models() 
PLANT_MODEL = MODELS.get('plant')
VALORISATION_MODEL = MODELS.get('valorisation')
CONSUMER_MODEL = MODELS.get('consumer')

def run_plant_prediction(image_data: bytes):
    """Exécute la prédiction YOLO pour les plantes directement depuis le fichier en mémoire."""
    
    if not PLANT_MODEL:
        
        return "Inconnu", {"label": "Service IA indisponible"}, [], None
    
    nparr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR) # Décodage ultra-rapide
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = PLANT_MODEL(image, conf=0.25)
    
    if not results or len(results[0].boxes) == 0:
        # return "Sain", {"label": "Sain", "confidence": 100.0, "pathologies": []}, [], None
        return "Inconnu", {"label": "Aucune maladie détectée"}, [], None

    result = results[0]
    original_names = result.names.copy()
    
    # --- Mapping pour l'IMAGE (Codes courts) ---
    short_names_for_plot = {id: SHORT_CODE_MAP.get(name, name) for id, name in original_names.items()}
    result.names = short_names_for_plot
    im_array = result.plot() 
    result.names = original_names
    # --- Traitement des détections (Traductions et filtrage) ---
    detections = []
    for box in result.boxes:
        cls_id = int(box.cls[0])
        name_en = original_names[cls_id]
        name_fr = TRANSLATION_MAP.get(name_en, "Inconnu")
        detections.append({
            "name_en": name_en,
            "name_fr": name_fr,
            "conf": round(float(box.conf[0]) * 100, 2),
            "coords": [round(x, 1) for x in box.xyxy[0].tolist()]
        })

    # --- Extraction de la maladie principale (Meilleur box) ---
    best_det = detections[0]
    eng_name = best_det["name_en"]
    disease_fr = best_det["name_fr"]
    short_code = SHORT_CODE_MAP.get(eng_name, "UNK")

    # --- Liste des pathologies pour le RAG (Uniques et filtrées) ---
    exclude = ["Tomato leaf", "Bell_pepper leaf", "Blueberry leaf"]
    pathologies_fr = list(dict.fromkeys([
        d["name_fr"] for d in detections if d["name_en"] not in exclude
    ]))
    
    # --- Extraction de la culture ---
    crop_name = "Inconnu"
    for eng_prefix, fr_crop in CROP_MAP.items():
        if eng_name.startswith(eng_prefix):
            crop_name = fr_crop
            break

    # Sauvegarde physique de l'image annotée
    image_path = save_diagnostic_image(im_array)

    detection_details = {
        "short_code": short_code,        
        "full_name_en": eng_name,
        "label": disease_fr,
        "culture": crop_name,
        "confidence": best_det["conf"],
        "pathologies": pathologies_fr,
        "boxes": [
            {
                "coords": d["coords"],
                "label": d["name_fr"]
            } for d in detections
        ]
    }
    print("image_path",image_path)
    # Récupérer le chemin actuel pour le log MLflow
    current_model_path = os.getenv("PLANT_MODEL_PATH", "Inconnu")

    # Logging MLflow via utilitaire
    # track_diagnostic(
    #    run_name="Plant_Diagnostic",
    #    model_type="YOLO_Plant",
    #    model_path=current_model_path,
    #    metrics={"confidence": best_det["conf"]},
    #    params={"disease_detected": disease_fr, "crop": crop_name},
    #    image_path=image_path
    #)

    return disease_fr, detection_details, pathologies_fr ,image_path

async def get_rag_ordonnance(pathologies: list, culture: str = None):
    """
    Récupère les recommandations RAG en incluant la culture pour plus de précision.
    """
    from src.api.v1.services import rag_service
    return await rag_service.get_ordonnance(pathologies, culture)


def run_valorisation_prediction(image_data: bytes):
    """Exécute la prédiction YOLO pour le contrôle qualité (Valorisation)."""
    
    if not VALORISATION_MODEL:
        return {}, 0.0, 0.0, "ERREUR", {"label": "Service IA indisponible"}, None

    # Chargement de l'image
    nparr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR) # Décodage ultra-rapide
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = VALORISATION_MODEL(image, conf=0.25)
    
    visual_defects = {}
    healthy_score = 1.0
    taux_defauts = 0.0
    decision = "DIRECT_EMBALLAGE"
    detection_details = {"label": "Sain", "confidence": 1.0, "boxes": []}
    image_path = None

    if results and len(results[0].boxes) > 0:
        result = results[0]
        
        # 1. Analyser toutes les détections
        detections = []
        visual_defects = {}
        defects_count = 0
        
        for box in result.boxes:
            cls_id = int(box.cls[0])
            label = result.names[cls_id]
            conf = round(float(box.conf[0]), 2)
            coords = [round(x, 1) for x in box.xyxy[0].tolist()]
            
            detections.append({
                "label": label,
                "confidence": conf,
                "coords": coords
            })

            if label.lower() != "sain":
                defects_count += 1
                visual_defects[label] = visual_defects.get(label, 0) + 1
        
        total_items = len(detections)
        taux_defauts = (defects_count / total_items) if total_items > 0 else 0
        healthy_score = 1.0 - taux_defauts
        
        # 2. Générer l'image annotée (Plot)
        im_array = result.plot()
        image_path = save_diagnostic_image(im_array)

        # Décision automatique : si plus de 20% de défauts -> Tri mécanique
        if taux_defauts > 0.2:
            decision = "MECANIQUE"
        
        detection_details = {
            "label": "Mixed" if defects_count > 0 else "Sain",
            "confidence": round(float(1.0 - taux_defauts), 2),
            "boxes": detections
        }

    # Logging MLflow via utilitaire
    metrics = {"healthy_score": healthy_score, "taux_defauts": taux_defauts}
    # Log dynamique des défauts
    for label, count in visual_defects.items():
        metrics[f"nb_{label}"] = count

    # Récupérer le chemin actuel pour le log MLflow
    current_model_path = os.getenv("VALORISATION_MODEL_PATH", "Inconnu")

   # track_diagnostic(
    #    run_name="Valorisation_Diagnostic",
     #   model_type="YOLO_Valorisation",
      #  model_path=current_model_path,
       # metrics=metrics,
        #params={"decision": decision},
        #image_path=image_path
    #)

    return visual_defects, healthy_score, taux_defauts, decision, detection_details, image_path

def run_freshness_prediction(image_data: bytes):
    """
    Exécute la prédiction YOLO pour classer le produit : Frais (Fresh) ou Pourri (Rotten).
    Utilise OpenCV pour un prétraitement rapide.
    """
    
    if not CONSUMER_MODEL:
        return "Inconnu", 0.0, {"label": "Service IA indisponible"}, None

   
    np_arr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Inférence YOLO
   
    results = CONSUMER_MODEL(image, conf=0.30)
    
    if not results or len(results[0].boxes) == 0:
        return "Indéterminé", 0.0, {"label": "Aucun produit détecté"}, None

    result = results[0]
   
    cls_id = int(result.boxes[0].cls[0])
    label_en = result.names[cls_id] # "Fresh" ou "Rotten"
    confidence = float(result.boxes[0].conf[0])

    if "fresh" in label_en.lower():
        freshness_score = round(confidence, 2)
    else:
        freshness_score = round(1.0 - confidence, 2)

    # Traduction simple pour le consommateur
    status_map = {"Fresh": "Frais", "Rotten": "pourri", "fresh": "Frais", "rotten": "pourri"}
    label_fr = status_map.get(label_en, label_en)

    # 4. Génération de l'image annotée pour le retour visuel client
    im_array = result.plot()
    image_path = save_diagnostic_image(im_array)

    detection_details = {
        "label": label_fr,
        "confidence": round(confidence, 2),
        "status_code": "GREEN" if "fresh" in label_en.lower() else "RED",
        "image_url": image_path,
        "freshness_score": freshness_score
    }

    return label_fr, freshness_score, detection_details, image_path