import os
import torch
import yaml
from ultralytics import YOLO

# ==========================================================
# 1. CONFIGURATION DU PROJET
# ==========================================================
TYPE_ENTRAINEMENT = "PRODUCTION" # ou "VALORISATION"

if TYPE_ENTRAINEMENT == "PRODUCTION":
    MODEL_TYPE = 'yolov10s.pt'  # Small pour les détails des maladies
    YAML_PATH = '/kaggle/working/maladies.yaml'
    PROJECT_NAME = 'EcoAgronomist_Maladies'
else:
    MODEL_TYPE = 'yolov10n.pt'  # Nano pour la vitesse sur les fruits
    YAML_PATH = '/kaggle/working/anomalies.yaml'
    PROJECT_NAME = 'EcoAgronomist_Anomalies'

OUTPUT_DIR = "/kaggle/working/results"

# ==========================================================
# 2. PATCH DE SÉCURITÉ PYTORCH 2.6
# ==========================================================
import torch.nn as nn
from ultralytics.nn.modules.conv import Conv
from ultralytics.nn.modules.block import C2f, Bottleneck, SPPF
torch.serialization.add_safe_globals([Conv, C2f, Bottleneck, SPPF, nn.modules.container.Sequential])

def safe_load(weights):
    if not os.path.exists(weights):
        os.system(f'wget https://github.com/THU-MIG/yolov10/releases/download/v1.1/{weights}')
    
    original_load = torch.load
    try:
        torch.load = lambda *args, **kwargs: original_load(*args, **kwargs, weights_only=False)
        return YOLO(weights)
    finally:
        torch.load = original_load

# ==========================================================
# 3. LANCEMENT DE L'ENTRAÎNEMENT
# ==========================================================
model = safe_load(MODEL_TYPE)

results = model.train(
    data=YAML_PATH,
    epochs=50,
    imgsz=640,
    batch=16,
    name=PROJECT_NAME,
    project=OUTPUT_DIR,
    device=0,         # GPU T4
    workers=4,
    exist_ok=True,
    optimizer='AdamW', # Très efficace pour les plantes
    lr0=0.01,         # Taux d'apprentissage initial
    augment=True      # Active les augmentations (mosaïque, flou) pour le terrain
)

print(f"✅ Entraînement {TYPE_ENTRAINEMENT} terminé !")