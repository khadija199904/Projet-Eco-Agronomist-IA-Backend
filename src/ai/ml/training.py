
import os
import torch
from ultralytics import YOLO, RTDETR

import yaml
from dotenv import load_dotenv
import glob




load_dotenv()

# --- Dataset Setup  ---
def setup_dataset(dataset_name_dir):
    """
    Prépare le dataset et synchronise le fichier nettoyé s'il existe.
    """
    # 1. Chemins de base
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    dataset_root = os.path.join(project_root, "data", "silver", dataset_name_dir)
    config_dir = os.path.join(project_root, "src/ml/configml")
    os.makedirs(config_dir, exist_ok=True)

    if not os.path.exists(dataset_root):
        raise FileNotFoundError(f"Dataset non trouvé : {dataset_root}")

    # 2. Définition des fichiers cibles dans configml
    fixed_yaml_name = f"{dataset_name_dir.replace('-', '_')}_fixed.yaml"
    cleaned_yaml_name = f"{dataset_name_dir.replace('-', '_')}_fixed_cleaned.yaml"
    
    target_fixed_path = os.path.join(config_dir, fixed_yaml_name)
    target_cleaned_path = os.path.join(config_dir, cleaned_yaml_name)

    # 3. VERIFICATION
    source_cleaned = os.path.join(dataset_root, "data_cleaned.yaml")

    if os.path.exists(source_cleaned):
        print(f"✨ Fichier nettoyé détecté dans les données : {source_cleaned}")
        with open(source_cleaned, 'r') as f:
            clean_config = yaml.safe_load(f)
        
        # On force la mise à jour du chemin pour Ultralytics
        clean_config['path'] = dataset_root
        
        # On le sauvegarde proprement dans configml
        with open(target_cleaned_path, 'w') as f:
            yaml.dump(clean_config, f, default_flow_style=False)
            
        print(f"✅ Dataset NETTOYÉ synchronisé : {target_cleaned_path}")
        return target_cleaned_path

    # 4. Si pas de nettoyé, on crée le fichier 'fixed' standard
    original_yaml_path = os.path.join(dataset_root, "data.yaml")
    if not os.path.exists(original_yaml_path):
        yaml_files = glob.glob(os.path.join(dataset_root, "**", "data.yaml"), recursive=True)
        original_yaml_path = yaml_files[0] if yaml_files else None

    if not original_yaml_path:
        raise FileNotFoundError(f"Aucun data.yaml trouvé pour {dataset_name_dir}")

    with open(original_yaml_path, 'r') as f:
        config = yaml.safe_load(f)

    # Reconstruction de la config pour Ultralytics
    new_config = {
        'path': dataset_root,
        'train': os.path.relpath(os.path.join(dataset_root, config.get('train', 'train/images')), dataset_root),
        'val': os.path.relpath(os.path.join(dataset_root, config.get('val', config.get('valid', 'val/images'))), dataset_root),
        'test': os.path.relpath(os.path.join(dataset_root, config.get('test', 'test/images')), dataset_root)
    }
    
    # Copie des noms et nombre de classes
    for key, value in config.items():
        if key not in ['path', 'train', 'val', 'valid', 'test']:
            new_config[key] = value

    with open(target_fixed_path, 'w') as f:
        yaml.dump(new_config, f, default_flow_style=False)

    print(f" Nouveau fichier config créé (Standard) : {target_fixed_path}")
    return target_fixed_path



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
        cleaned_path = data_yaml_path.replace(".yaml", "_cleaned.yaml")
        if os.path.exists(cleaned_path):
           data_yaml_path = cleaned_path
           print(f"--- MODE NETTOYAGE ACTIVÉ : {data_yaml_path} ---")
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
        weight_decay = 0.0005 
        
    else:
        optimizer = 'auto'
        lr0 = 0.01
        warmup_epochs = 3.0
        weight_decay = 0.0005 
      
 
    model.train(
                    data=data_yaml_path, 
                    epochs=epochs,
                    imgsz=imgsz,
                    batch=-1,
                    name=f"{project_name}_{algo}_Optim",
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
    train_eco_agronomist(
         pole="PRODUCTION", 
         algo="YOLO", 
        epochs=100
     )

    # You can uncomment and test other configurations if needed
    # Test 1 : Pôle Production avec RT-DETR (Le plus moderne)
    # train_eco_agronomist(
    #     pole="PRODUCTION", 
    #     algo="RTDETR", 
    #     epochs=50
    # )
     # # Test 2 : Pôle Valorisation avec YOLO Nano (Le plus rapide pour PWA)
    # train_eco_agronomist(
    #   pole="VALORISATION", 
    #  algo="YOLO", 
    #  epochs=100
    # )

    # # Test 2 : Pôle Valorisation avec YOLO Nano (Le plus rapide pour PWA)
    #train_eco_agronomist(
     #   pole="CONSOMMATION", 
     #   algo="YOLO", 
      #  epochs=100
     #)