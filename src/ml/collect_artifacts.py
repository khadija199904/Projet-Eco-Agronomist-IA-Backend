import shutil
import os
from pathlib import Path
from ultralytics import YOLO, RTDETR

def get_best_run_path(base_results_dir: str, run_name: str) -> Path:
    """Cherche récursivement le dossier de run pour éviter les erreurs de chemin relatif."""
    for path in Path(base_results_dir).rglob(run_name):
        if (path / "weights" / "best.pt").exists():
            return path
    return None

def save_and_export_ml_artifacts(
    run_name: str, 
    artifact_name: str, 
    model_type: str = "YOLO",
    version: str = "v1",
    base_results_dir: str = ".", # Cherche partout dans le projet
    destination_dir: str = "artifacts/models_saved"
):
    """
    Version optimisée : Détection auto + Export ONNX compressé.
    """
    # 1. Localisation intelligente du dossier de run
    run_path = get_best_run_path(base_results_dir, run_name)
    
    if not run_path:
        print(f" Erreur : Dossier '{run_name}' avec 'best.pt' introuvable dans {base_results_dir}")
        return

    dest_path = Path(destination_dir) / f"{artifact_name}_{version}"
    dest_path.mkdir(parents=True, exist_ok=True)

    source_pt = run_path / "weights" / "best.pt"
    dest_pt = dest_path / f"{artifact_name}.pt"

    # 2. Copie et Export
    shutil.copy(source_pt, dest_pt)
    print(f" PyTorch sauvegardé : {dest_pt}")

    print(f" Conversion ONNX optimisée pour PWA (Web/Mobile)...")
    try:
        model_loader = RTDETR if model_type == "RTDETR" else YOLO
        model = model_loader(str(dest_pt))
        
        # Optimisations spécifiques pour le déploiement Web (PWA)
        onnx_path = model.export(
            format='onnx', 
            imgsz=640, 
            simplify=True, 
            opset=12, # Meilleure compatibilité avec onnxruntime-web
        )
        # Déplacer l'ONNX vers le dossier final
        shutil.move(onnx_path, dest_path / f"{artifact_name}.onnx")
        print(f"🚀 ONNX optimisé prêt pour le déploiement.")
    except Exception as e:
        print(f"⚠️ Export ONNX échoué : {e}")

    # 3. Collecte sélective des graphiques
    metrics = ["results.png", "confusion_matrix.png", "F1_curve.png"]
    for m in metrics:
        if (run_path / m).exists():
            shutil.copy(run_path / m, dest_path / m)

if __name__ == "__main__":
    # Plus besoin de deviner le chemin complet, on donne juste le nom du dossier final
    save_and_export_ml_artifacts(
        run_name="Prod_Maladies_YOLO", 
        artifact_name="agrivision_maladies_s",
        model_type="YOLO26"
    )