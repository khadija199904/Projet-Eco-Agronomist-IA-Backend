import os
import torch
from ultralytics import YOLO, RTDETR

def train_eco_agronomist(pole="PRODUCTION", algo="YOLO", dataset_yaml="data.yaml", epochs=50):
    """
    Lance l'entraînement selon le pôle et l'algorithme choisis.
    poles: "PRODUCTION" (Maladies) ou "VALORISATION" (Fruits/Anomalies)
    algos: "YOLO", "RTDETR", "MOBILENET", "DETECTRON2"
    """
    
    print(f" Initialisation de l'entraînement : Pôle {pole} avec {algo}...")
    
    if pole == "PRODUCTION":
        project_name = "Prod_Maladies"
        if algo == "YOLO":
            model_path = 'yolov10s.pt'
            model = YOLO(model_path)
        elif algo == "RTDETR":
            
            model_path = 'rtdetr-l.pt' 
            model = RTDETR(model_path)
        
    elif pole == "VALORISATION":
        project_name = "Val_Anomalies"
        algo == "YOLO"
        model_path = 'yolov10n.pt' # Nano pour la vitesse mobile
        model = YOLO(model_path)
        

    # --- Lancement de l'entraînement ---
    optimizer = 'AdamW' if algo == "RTDETR" else 'auto'
    
    results = model.train(
        data=dataset_yaml,
        epochs=epochs,
        imgsz=640,
        batch=16,
        name=f"{project_name}_{algo}",
        project="./results",
        device=0, # GPU NVIDIA local
        optimizer=optimizer,
        augment=True,
        exist_ok=True
    )
    
    print(f"Entraînement terminé. Résultats sauvegardés dans ./results/{project_name}_{algo}")
    return model


if __name__ == "__main__":
    # Vérifie si le GPU est disponible
    device = "0" if torch.cuda.is_available() else "cpu"
    print(f"Entraînement sur : {device}")

    # Test 1 : Pôle Production avec RT-DETR (Le plus moderne)
    train_eco_agronomist(
        pole="PRODUCTION", 
        algo="RTDETR", 
        dataset_yaml="maladies.yaml", 
        epochs=100
    )

    # Test 2 : Pôle Valorisation avec YOLO Nano (Le plus rapide pour PWA)
    # train_eco_agronomist(
    #     pole="VALORISATION", 
    #     algo="YOLO", 
    #     dataset_yaml="anomalies.yaml", 
    #     epochs=50
    # )