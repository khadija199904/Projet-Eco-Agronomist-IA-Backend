import shutil
from pathlib import Path
from ultralytics import YOLO

def save_and_export_ml_artifacts(
    run_dir: str, 
    artifact_name: str, 
    version: str = "v1",
    destination_dir: str = "src/ml/artifacts/models_saved"
):
    """
    Sauvegarde le modèle, exporte en ONNX et récupère les métriques.
    """
    run_path = Path(run_dir)
    dest_path = Path(destination_dir)
    dest_path.mkdir(parents=True, exist_ok=True)

    # 1. Chemins des fichiers
    source_pt = run_path / "weights" / "best.pt"
    final_name = f"{artifact_name}_{version}"
    dest_pt = dest_path / f"{final_name}.pt"

    if not source_pt.exists():
        print(f"❌ Erreur : Fichier source introuvable : {source_pt}")
        return

    # 2. Copie du fichier PyTorch (.pt)
    shutil.copy(source_pt, dest_pt)
    print(f"Modèle PyTorch sauvegardé : {dest_pt}")

    # 3. Exportation en format ONNX (Optimisé pour l'inférence/FastAPI)
    print(f" Conversion de {dest_pt.name} en format ONNX en cours...")
    try:
        model = YOLO(str(dest_pt))
        onnx_path = model.export(format='onnx', simplify=True)
        
        # Le fichier ONNX est créé au même endroit avec le même nom de base
        print(f" Modèle ONNX généré avec succès.")
    except Exception as e:
        print(f" Erreur lors de l'export ONNX : {e}")

    # 4. Copie des métriques (Confusion Matrix, Results)
    metrics = ["confusion_matrix.png", "results.png"]
    for metric_file in metrics:
        metric_source = run_path / metric_file
        if metric_source.exists():
            shutil.copy(metric_source, dest_path / f"{final_name}_{metric_file}")
            print(f" Métrique sauvegardée : {metric_file}")

if __name__ == "__main__":
    save_and_export_ml_artifacts(
        run_dir="src/ml/runs/detect/parking_yolov8_plant5",
        artifact_name="maladies_plant5",
        version="v1"
    )