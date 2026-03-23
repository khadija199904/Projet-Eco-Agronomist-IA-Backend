import os
import yaml
import glob

def clean_dataset(dataset_name_dir, min_instances=10):
    """
    Analyse le dataset et suggère de supprimer les classes trop rares.
    """
    project_root = os.path.abspath(os.path.join(os.getcwd()))
    dataset_root = os.path.join(project_root, "data", "silver", dataset_name_dir)
    yaml_path = os.path.join(dataset_root, "data.yaml")

    if not os.path.exists(yaml_path):
        print(f"Erreur : {yaml_path} non trouvé.")
        return

    with open(yaml_path, 'r') as f:
        config = yaml.safe_load(f)

    # 1. Compter les instances par classe dans les labels de train
    label_files = glob.glob(os.path.join(dataset_root, "train/labels", "*.txt"))
    class_counts = {i: 0 for i in range(len(config['names']))}

    for lb in label_files:
        with open(lb, 'r') as f:
            for line in f:
                # Ajout d'une vérification pour les lignes vides ou avec seulement des espaces
                if line.strip(): # Ensure the line is not empty or just whitespace
                    class_id = int(line.split()[0])
                    class_counts[class_id] += 1

    # 2. Identifier les classes à garder
    classes_to_keep = {i: name for i, name in enumerate(config['names']) if class_counts[i] >= min_instances}
    classes_to_drop = {i: name for i, name in enumerate(config['names']) if class_counts[i] < min_instances}

    print(f"--- ANALYSE DU DATASET : {dataset_name_dir} ---")
    print(f"Classes conservées ({len(classes_to_keep)}) : {list(classes_to_keep.values())}")
    print(f"Classes supprimées ({len(classes_to_drop)}) car < {min_instances} instances : {list(classes_to_drop.values())}")

    # 3. Créer un nouveau YAML "Clean"
    # Note : Le nettoyage des fichiers .txt eux-mêmes est complexe (réindexation).
    # Le plus simple est de mettre à jour ton dictionnaire 'names' pour ignorer les classes vides.
    
    new_config = config.copy()
    # On garde les IDs originaux pour ne pas corrompre les fichiers .txt, 
    # mais on peut renommer les classes inutiles en 'ignore'
    for i in range(len(config['names'])):
        if i not in classes_to_keep:
            new_config['names'][i] = f"ignore_{config['names'][i]}"

    new_yaml_path = yaml_path.replace(".yaml", "_cleaned.yaml")
    with open(new_yaml_path, 'w') as f:
        yaml.dump(new_config, f)

    print(f"Nouveau fichier de config créé : {new_yaml_path}")

if __name__ == "__main__":
    # Test sur ton dataset de Valorisation
    clean_dataset("fruits-vegetables-disease-detection", min_instances=10)