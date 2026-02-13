from tasks.session_spark import get_spark_session
from pyspark.sql.functions import col
import os
import shutil

# 1. Initialiser la session Spark via ton module
spark = get_spark_session("Silver_Layer_Filtering")

# 2. Configuration des dossiers
BRONZE_DIR = "data/bronze/plant-doc/PlantDoc-Dataset"
SILVER_DIR = "data/silver/filtered_images"

# 3. Dictionnaire des plantes cibles pour Agadir
TARGET_PLANTS = {
    "Poivron": ["poivron", "pepper", "bell pepper"],
    "Agrumes": ["agrumes", "citrus", "orange", "lemon", "citron", "mandarine", "clementine"],
    "Haricot": ["haricot", "bean"],
    "Myrtille": ["myrtille", "blueberry"],
    "Mais": ["mais", "corn", "maize"],
    "Courgette": ["courgette", "zucchini", "squash"],
    "Aubergine": ["aubergine", "eggplant"]
}

def filter_and_organize(split_name):
    """
    Filtre les images du dossier Bronze (train ou test) 
    et les organise par catégorie dans Silver.
    """
    print(f"\n--- Traitement du dossier : {split_name} ---")
    
    source_path = os.path.join(BRONZE_DIR, split_name)
    destination_path = os.path.join(SILVER_DIR, split_name)

    # Créer une regex pour le filtrage Spark (ex: "pepper|orange|banana...")
    all_keywords = [kw for sublist in TARGET_PLANTS.values() for kw in sublist]
    regex_pattern = "|".join(all_keywords)

    # A. Scanner les chemins de fichiers avec Spark (Rapide)
    df = spark.read.format("binaryFile") \
        .option("recursiveFileLookup", "true") \
        .load(source_path) \
        .select("path")

    # B. Filtrer les chemins contenant nos mots-clés
    filtered_df = df.filter(col("path").rlike(f"(?i){regex_pattern}"))
    image_paths = filtered_df.collect()

    # C. Copier les fichiers vers la couche Silver
    for row in image_paths:
        full_path = row['path'].replace("file:", "") # Nettoyage du chemin
        file_name = os.path.basename(full_path)
        
        # Trouver la catégorie correcte pour le dossier
        category = "Autres"
        for plant, keywords in TARGET_PLANTS.items():
            if any(kw in full_path.lower() for kw in keywords):
                category = plant
                break
        
        # Créer le dossier destination (ex: data/silver/filtered_images/train/Poivron)
        final_dest = os.path.join(destination_path, category)
        os.makedirs(final_dest, exist_ok=True)
        
        # Copie physique
        shutil.copy(full_path, os.path.join(final_dest, file_name))

    print(f"Terminé : {len(image_paths)} images filtrées pour {split_name}.")

if __name__ == "__main__":
    # On lance le traitement pour 'train'
    filter_and_organize("train")
    
    # On lance le traitement pour 'test'
    filter_and_organize("test")