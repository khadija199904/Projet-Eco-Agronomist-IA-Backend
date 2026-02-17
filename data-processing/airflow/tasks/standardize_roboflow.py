import os
import shutil

def standardize_roboflow():
    # Chemins
    SRC_DIR = "/opt/airflow/data/raw/robo_pepper_plant"
    DST_DIR = "/opt/airflow/data/raw/roboflow_standardized"
    
    mapping = {
        'train': 'train',
        'valid': 'val',
        'test': 'val'   
    }

    if not os.path.exists(SRC_DIR):
        print(f"Source {SRC_DIR} introuvable.")
        return

    if os.path.exists(DST_DIR):
        shutil.rmtree(DST_DIR)
    
    # Création de la structure : images/(train|val) et labels/(train|val)
    for folder in ['images', 'labels']:
        for split in ['train', 'val']:
            os.makedirs(os.path.join(DST_DIR, folder, split), exist_ok=True)
    
    # 2. Copie du fichier data.yaml (indispensable pour le filtrage Spark)
    src_yaml = os.path.join(SRC_DIR, 'data.yaml')
    if os.path.exists(src_yaml):
        shutil.copy2(src_yaml, os.path.join(DST_DIR, 'data.yaml'))
        print("Fichier data.yaml copié avec succès.")
    
    # Initialisation des compteurs pour éviter d'écraser les fichiers lors de la fusion
    counters = {'train': 0, 'val': 0}

    for src_split, dst_split in mapping.items():
        src_split_path = os.path.join(SRC_DIR, src_split)
        if not os.path.exists(src_split_path):
            print(f"Attention : Dossier source {src_split} absent, passage...")
            continue

        img_dir = os.path.join(src_split_path, "images")
        if not os.path.exists(img_dir):          continue
        
        files = [f for f in os.listdir(img_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        print(f"Fusion de Roboflow '{src_split}' vers Silver '{dst_split}' ({len(files)} fichiers)...")

        for old_name in sorted(files):
            # Utilisation du compteur global pour ce split de destination
            idx = counters[dst_split]
            extension = os.path.splitext(old_name)[1]
            
            # Nouveau nom unique : robo_val_00001, robo_val_00002, etc.
            new_base_name = f"robo_{dst_split}_{idx:05d}"
            new_img_name = new_base_name + extension
            new_lbl_name = new_base_name + ".txt"
            
            # Chemins sources
            old_img_path = os.path.join(img_dir, old_name)
            old_lbl_path = os.path.join(src_split_path, "labels", os.path.splitext(old_name)[0] + ".txt")

            # Chemins destinations
            dst_img_path = os.path.join(DST_DIR, "images", dst_split, new_img_name)
            dst_lbl_path = os.path.join(DST_DIR, "labels", dst_split, new_lbl_name)

            # Copie physique
            shutil.copy2(old_img_path, dst_img_path)
            if os.path.exists(old_lbl_path):
                shutil.copy2(old_lbl_path, dst_lbl_path)
            
            # Incrémenter le compteur du split de destination
            counters[dst_split] += 1

    print(f"Succès ! Roboflow est standardisé dans {DST_DIR}")
    print(f"Statistiques finales : Train={counters['train']} images | Val (Fusionné)={counters['val']} images")

if __name__ == "__main__":
    standardize_roboflow()