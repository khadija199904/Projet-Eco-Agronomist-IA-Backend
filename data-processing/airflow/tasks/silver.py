import os
import shutil
import yaml
from session_spark import get_spark_session
from pyspark.sql.functions import col, udf
from pyspark.sql.types import StringType

# Initialisation de Spark
spark = get_spark_session("Silver_Layer_Processing")

TARGET_IDS = ["2", "6", "7", "8", "11", "12", "13", "15", "16", "18", "19", "21", "22", "24", "25", "28"]

ORIGINAL_NAMES = {
    0: "Cherry leaf", 1: "Peach leaf", 2: "Corn leaf blight", 3: "Apple rust leaf",
    4: "Potato leaf late blight", 5: "Strawberry leaf", 6: "Corn rust leaf",
    7: "Tomato leaf late blight", 8: "Tomato mold leaf", 9: "Potato leaf early blight",
    10: "Apple leaf", 11: "Tomato leaf yellow virus", 12: "Blueberry leaf",
    13: "Tomato leaf mosaic virus", 14: "Raspberry leaf", 15: "Tomato leaf bacterial spot",
    16: "Squash Powdery mildew leaf", 17: "grape leaf", 18: "Corn Gray leaf spot",
    19: "Tomato Early blight leaf", 20: "Apple Scab Leaf", 21: "Tomato Septoria leaf spot",
    22: "Tomato leaf", 23: "Soyabean leaf", 24: "Bell_pepper leaf spot",
    25: "Bell_pepper leaf", 26: "grape leaf black rot", 27: "Potato leaf",
    28: "Tomato two spotted spider mites leaf"
}

def filter_labels(content):
    """Filtre les lignes du fichier label selon les TARGET_IDS."""
    if not content: 
        return None
    lines = content.strip().split('\n')
    valid_lines = [l for l in lines if l.split() and l.split()[0] in TARGET_IDS]
    return "\n".join(valid_lines) if valid_lines else None

def copy_files_worker(partition):
    """Fonction exécutée sur les workers pour copier les images et écrire les labels."""
    
    BRONZE_DIR = "/opt/airflow/data/bronze/plant-doc"
    SILVER_DIR = "/opt/airflow/data/silver"
    
    for row in partition:
        split, filename, content = row
        img_name = filename.replace(".txt", ".jpg")
        
        # Chemins
        src_img = os.path.join(BRONZE_DIR, "images", split, img_name)
        dst_img = os.path.join(SILVER_DIR, split, "images", img_name)
        dst_lbl = os.path.join(SILVER_DIR, split, "labels", filename)
        
        if os.path.exists(src_img):
            shutil.copy(src_img, dst_img)
            with open(dst_lbl, "w") as f:
                f.write(content)

def process_silver():
    BRONZE_DIR = "/opt/airflow/data/bronze/plant-doc"
    SILVER_DIR = "/opt/airflow/data/silver"

    # 1. Nettoyage et création des dossiers (Côté Driver)
    if os.path.exists(SILVER_DIR): shutil.rmtree(SILVER_DIR)
    for split in ['train', 'val']:
        os.makedirs(f"{SILVER_DIR}/{split}/images", exist_ok=True)
        os.makedirs(f"{SILVER_DIR}/{split}/labels", exist_ok=True)

    # 2. Lecture distribuée des labels avec Spark
    # On utilise wholeTextFiles pour lire (chemin, contenu)
    raw_files_rdd = spark.sparkContext.wholeTextFiles(f"{BRONZE_DIR}/labels/*/*.txt")

    # Transformation en DataFrame pour le traitement
    labels_df = raw_files_rdd.map(lambda x: (
        "train" if "train" in x[0] else "val",
        os.path.basename(x[0]),
        x[1]
    )).toDF(["split", "filename", "raw_content"])

    # 3. Filtrage avec UDF
    filter_udf = udf(filter_labels, StringType())
    silver_df = labels_df.withColumn("filtered_content", filter_udf(col("raw_content"))) \
                         .filter(col("filtered_content").isNotNull()) \
                         .select("split", "filename", "filtered_content")

    # 4. Action : Distribution de la copie des fichiers
    silver_df.rdd.foreachPartition(copy_files_worker)

    # 5. Création du YAML (Côté Driver)
    yaml_content = {
        'path': '/opt/airflow/data/silver',
        'train': 'train/images',
        'val': 'val/images',
        'nc': 29,
        'names': ORIGINAL_NAMES
    }
    with open(os.path.join(SILVER_DIR, 'dataset.yaml'), 'w') as f:
        yaml.dump(yaml_content, f, default_flow_style=False)

    print("Couche Silver terminée avec PySpark.")

if __name__ == "__main__":
    process_silver()