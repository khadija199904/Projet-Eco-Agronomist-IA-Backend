import mlflow
import os
import torch
from ultralytics import YOLO, RTDETR

import yaml
from dotenv import load_dotenv
import glob

from src.data.kaggle_loader import download_kaggle_dataset
from .tracking import setup_mlflow

load_dotenv()

# --- Dataset Setup  ---
def setup_dataset(dataset_name):
    """Downloads the Kaggle dataset and prepares its YAML configuration."""
    
    dataset_root = download_kaggle_dataset(dataset_name)

    original_yaml_path = os.path.join(dataset_root, "dataset.yaml")
    
    if not os.path.exists(original_yaml_path):
        print(f"Error: dataset.yaml not found at {original_yaml_path}")
        yaml_files = glob.glob(os.path.join(dataset_root, "**", "data.yaml"), recursive=True)
        if yaml_files:
            original_yaml_path = yaml_files[0]
            print(f"Found dataset.yaml in subdirectory: {original_yaml_path}")
        else:
            raise FileNotFoundError(f"dataset.yaml not found for {dataset_name}")

    with open(original_yaml_path, 'r') as f:
        config = yaml.safe_load(f)

    config['path'] = dataset_root
    config['train'] = 'train/images'
    config['val'] = 'val/images'

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    config_dir = os.path.join(project_root, "src/ml/configml")
    os.makedirs(config_dir, exist_ok=True)
    
    new_yaml_filename = f"{dataset_name.split('/')[-1].replace('-', '_')}_fixed.yaml"
    new_yaml_path = os.path.join(config_dir, new_yaml_filename)

    with open(new_yaml_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)

    print(f"New config file created: {new_yaml_path}")
    return new_yaml_path


def train_eco_agronomist(pole="PRODUCTION", algo="YOLO", epochs=50):
    """
    Lance l'entraînement selon le pôle et l'algorithme choisis.
    poles: "PRODUCTION" (Maladies) ou "VALORISATION" (Fruits/Anomalies)
    algos: "YOLO", "RTDETR"
    """
    setup_mlflow()
    dataset_1 = "khadijaelabbioui/agrivision-plant-disease"
    dataset_2 = "khadijaelabbioui/fruit-disease-detection"
    dataset_3 = "khadijaelabbioui/fresh-rotten-1"
    

    print(f" Initialisation de l'entraînement : Pôle {pole} avec {algo}...")
    
    if pole == "PRODUCTION":
        project_name = "Prod_Maladies"
        data_yaml_path = setup_dataset(dataset_1) 
        
        model_path = 'yolo26s.pt' if algo == "YOLO" else 'rtdetr-l.pt'
        
    elif pole == "VALORISATION":
        project_name = "Val_Anomalies"
        data_yaml_path = setup_dataset(dataset_2) 
        
        model_path = 'yolo11n.pt' 
        if algo == "RTDETR":
            print(" RTDETR non configuré pour Valorisation. Utilisation de YOLO Nano par défaut.")
            algo = "YOLO"
    elif pole == "CONSOMMATION":
        project_name = "Conso_Fraicheur"
        data_yaml_path = setup_dataset(dataset_3)
        model_path = 'yolo26n.pt' 
        algo = "YOLO"
    else:
        raise ValueError("Pôle non reconnu")

    # 2. Chargement effectif du modèle
    if algo == "RTDETR":
        model = RTDETR(model_path)
    else:
        model = YOLO(model_path)
        

    # --- Lancement de l'entraînement ---
    if algo == "RTDETR":
        optimizer = 'AdamW'
        lr0 = 0.0005  # Lowered from 0.01 to prevent NaN
        warmup_epochs = 3 
        weight_decay = 0.0001
        imgsz = 480
        batch = 8
    else:
        optimizer = 'auto'
        lr0 = 0.01
        warmup_epochs = 3.0
        weight_decay = 0.0005 
        imgsz =640
        batch = 16
 
    results = model.train(
                    data=data_yaml_path, 
                    epochs=epochs,
                    imgsz=imgsz,
                    batch=batch,
                    name=f"{project_name}_{algo}",
                    project="./results",
                    device=0, # GPU NVIDIA local (lightning.ai)
                    optimizer=optimizer,
                    lr0=lr0, 
                    warmup_epochs=warmup_epochs,
                    weight_decay=weight_decay,
                    augment=True,
                    exist_ok=True,
                    plots=True,
                    save=True 
    
            )
    with mlflow.start_run(run_id=mlflow.last_active_run().info.run_id):
        mlflow.log_param("custom_pole", pole)
        mlflow.log_artifact("path/to/extra/file")
    
    print(f"Entraînement terminé. MLflow a enregistré la session. Résultats sauvegardés dans ./results/{project_name}_{algo}")
    return model


if __name__ == "__main__":
    print(f"Vérification CUDA : {torch.cuda.is_available()}")
    if torch.cuda.is_available():
       print(f"GPU détecté : {torch.cuda.get_device_name(0)}")
    
       # Test de calcul sur GPU
       x = torch.rand(5, 3).cuda()
       print("Test de calcul réussi sur GPU !")
    else:
       print("CUDA toujours indisponible. Vérifiez l'installation.")
    
    # Test : Pôle Production avec YOLO 
    # train_eco_agronomist(
    #     pole="PRODUCTION", 
    #     algo="YOLO", 
    #     epochs=100
    # )

    # You can uncomment and test other configurations if needed
    # Test 1 : Pôle Production avec RT-DETR (Le plus moderne)
   # train_eco_agronomist(
   #      pole="PRODUCTION", 
   #      algo="RTDETR", 
    #     epochs=30
    # )

    # Test 2 : Pôle Valorisation avec YOLO Nano (Le plus rapide pour PWA)
    train_eco_agronomist(
        pole="VALORISATION", 
        algo="YOLO", 
        epochs=100
    )