import mlflow
import os
import torch
from ultralytics import YOLO, RTDETR

import yaml
from dotenv import load_dotenv
import glob

# Removed: from src.data.kaggle_loader import download_kaggle_dataset
from .tracking import setup_mlflow

load_dotenv()

# --- Dataset Setup  ---
def setup_dataset(dataset_name_dir):
    """
    Prepares the dataset by using a local folder and generating its YAML configuration.
    
    Args:
        base_data_dir (str): The base directory where all local datasets are stored (e.g., 'data').
        dataset_name_sub_dir (str): The name of the subdirectory for the specific dataset
                                    (e.g., 'agrivision-plant-disease').
    """
    
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    dataset_root = os.path.join(project_root, "data", "silver", dataset_name_dir)
    
    if not os.path.exists(dataset_root):
        raise FileNotFoundError(f"local dataset not found at {dataset_root}. please ensure your dataset is placed there.")

    
    original_yaml_path = os.path.join(dataset_root, "data.yaml")
    if not os.path.exists(original_yaml_path):
        yaml_files = glob.glob(os.path.join(dataset_root, "**", "data.yaml"), recursive=True)
        if yaml_files:
            original_yaml_path = yaml_files[0]
            
            print(f"found data.yaml in subdirectory: {original_yaml_path}")
        else:
            raise FileNotFoundError(f"data.yaml or dataset.yaml not found for {dataset_name_dir} in {dataset_root}")

    with open(original_yaml_path, 'r') as f:
        config = yaml.safe_load(f)

    
    new_config = {}
    new_config['path'] = dataset_root # This sets the base path for ultralytics
    
    # Extract and normalize 'train', 'val', 'test' paths to be relative to the dataset_root
    # Ultralytics expects these to be relative to the 'path' entry.
    
    # Handle 'train'
    if 'train' in config:
        new_config['train'] = os.path.relpath(os.path.join(dataset_root, config['train']), dataset_root)
    else:
        new_config['train'] = 'train/images' # Default if not specified

    # Handle 'val' or 'valid' for validation set
    if 'val' in config:
        new_config['val'] = os.path.relpath(os.path.join(dataset_root, config['val']), dataset_root)
    elif 'valid' in config:
        new_config['val'] = os.path.relpath(os.path.join(dataset_root, config['valid']), dataset_root)
    else:
        new_config['val'] = 'val/images' # Default if neither specified

    # Handle 'test'
    if 'test' in config:
        new_config['test'] = os.path.relpath(os.path.join(dataset_root, config['test']), dataset_root)
    else:
        # Default if not specified, you might want to adjust this if your dataset doesn't have a test set
        new_config['test'] = 'test/images' 

    # Copy other non-path related keys (like names, nc)
    for key, value in config.items():
        if key not in ['path', 'train', 'val', 'valid', 'test']:
            new_config[key] = value

    config_dir = os.path.join(project_root, "src/ml/configml")
    os.makedirs(config_dir, exist_ok=True)
    
    
    new_yaml_filename = f"{dataset_name_dir.replace('-', '_')}_fixed.yaml"
    new_yaml_path = os.path.join(config_dir, new_yaml_filename)

    with open(new_yaml_path, 'w') as f:
        yaml.dump(new_config, f, default_flow_style=False)

    print(f"new config file created: {new_yaml_path}")
    return new_yaml_path



def train_eco_agronomist(pole="PRODUCTION", algo="YOLO", epochs=50):
    """
    Lance l'entraînement selon le pôle et l'algorithme choisis.
    poles: "PRODUCTION" (Maladies) ou "VALORISATION" (Fruits/Anomalies)
    algos: "YOLO", "RTDETR"
    """


    dataset_1_sub_dir = "detection_maladies_plantes"
    dataset_2_sub_dir = "fruits-vegetables-disease-detection"
    dataset_3_sub_dir = "Fresh-Rotten"
    

    print(f" Initialisation de l'entraînement : Pôle {pole} avec {algo}...")
    
    if pole == "PRODUCTION":
        project_name = "Prod_Maladies"
        data_yaml_path = setup_dataset(dataset_1_sub_dir) 
        model_path = 'yolo26s.pt' if algo == "YOLO" else 'rtdetr-l.pt'
        imgsz = 800
        
    elif pole == "VALORISATION":
        project_name = "Val_Anomalies"
        data_yaml_path = setup_dataset(dataset_2_sub_dir) 
        imgsz = 640
        model_path = 'yolo26n.pt' 
        if algo == "RTDETR":
            print(" RTDETR non configuré pour Valorisation. Utilisation de YOLO Nano par défaut.")
            algo = "YOLO"
    elif pole == "CONSOMMATION":
        project_name = "Conso_Fraicheur"
        data_yaml_path = setup_dataset(dataset_3_sub_dir)
        model_path = 'yolo26n.pt' 
        algo = "YOLO"
        imgsz = 640
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
        lr0 = 0.0005  
        warmup_epochs = 3 
       
    else:
        optimizer = 'auto'
        lr0 = 0.01
        warmup_epochs = 3.0
        weight_decay = 0.0005 
      
 
    results = model.train(
                    data=data_yaml_path, 
                    epochs=epochs,
                    imgsz=imgsz,
                    batch=-1,
                    name=f"{project_name}_{algo}_Opti",
                    project="./results",
                    device=0, # GPU NVIDIA local (lightning.ai)
                    optimizer=optimizer,
                    lr0=lr0, 
                    patience=20,
                    warmup_epochs=warmup_epochs,
                    weight_decay=weight_decay,
                    box=7.5,            # Augmente l'importance de la précision de la boîte
                    cls=1.5,            # Augmente l'importance de la classification
                    overlap_mask=True,

                    augment=True,
                    mosaic=1.0,   # Mélange les images pour apprendre les contextes variés
                    mixup=0.1,          # Superpose des images (excellent pour les maladies denses)
                    scale=0.5,          # Aide à détecter les objets de tailles différentes
                    
                    exist_ok=True,
                    plots=True,
                    save=True ,
                    cache=True
    
            )
    metrics = model.val()
    print(f"Top 1 Accuracy: {metrics.results_dict['metrics/mAP50(B)']}")    
   
    print(f"Entraînement terminé.  Résultats sauvegardés dans ./results/{project_name}_{algo}")
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
     # # Test 2 : Pôle Valorisation avec YOLO Nano (Le plus rapide pour PWA)
    train_eco_agronomist(
        pole="VALORISATION", 
      algo="YOLO", 
      epochs=100
    )

    # # Test 2 : Pôle Valorisation avec YOLO Nano (Le plus rapide pour PWA)
    # train_eco_agronomist(
     #   pole="CONSOMMATION", 
     #   algo="YOLO", 
     #   epochs=100
    # )