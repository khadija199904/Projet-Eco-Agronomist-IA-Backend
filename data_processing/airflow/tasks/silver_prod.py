import os
import shutil
import yaml
from session_spark import get_spark_session
from pyspark.sql.functions import col, udf
from pyspark.sql.types import StringType

# Initialisation de Spark 
spark = get_spark_session("Silver_Layer_Final_Fusion")

# --- 1. CONFIGURATION DU MAPPING DE RÉINDEXATION (0 à 17) ---

# Mapping PlantDoc (Kaggle) -> New ID
KAG_TO_SILVER = {
    "2": "0", "6": "1", "7": "2", "8": "3", "11": "4", "12": "5", 
    "13": "6", "15": "7", "16": "8", "18": "9", "19": "10", "21": "11", 
    "22": "12", "24": "13", "25": "14", "28": "15"
}

# Mapping Roboflow -> New ID (Fusion des classes communes + nouvelles)
ROBO_TO_SILVER = {
    "0": "7",   # Bacterial Spot -> Fusionné avec l'ID 7
    "1": "14",  # Bell_pepper leaf -> ID 14
    "2": "13",  # Bell_pepper leaf spot -> ID 13
    "3": "16",  # Nutrient Deficiencies -> ID 16
    "4": "17"   # White bugs -> ID 17
}

# Noms des classes pour le fichier YAML final
FINAL_NAMES = {
    0: "Corn leaf blight", 1: "Corn rust leaf", 2: "Tomato leaf late blight",
    3: "Tomato mold leaf", 4: "Tomato leaf yellow virus", 5: "Blueberry leaf",
    6: "Tomato leaf mosaic virus", 7: "Tomato leaf bacterial spot",
    8: "Squash Powdery mildew leaf", 9: "Corn Gray leaf spot",
    10: "Tomato Early blight leaf", 11: "Tomato Septoria leaf spot",
    12: "Tomato leaf", 13: "Bell_pepper leaf spot", 14: "Bell_pepper leaf",
    15: "Tomato two spotted spider mites leaf",
    16: "Nutrient Deficiencies", 17: "White bugs"
}

BRONZE_DIR = "/opt/airflow/data/bronze"
SILVER_DIR = "/opt/airflow/data/silver/detection_maladies_plantes"


# --- 2. LOGIQUE DE FILTRAGE ET RÉINDEXATION (UDF) ---

def filter_and_reindex_udf(content, source):
    if not content: return None
    lines = content.strip().split('\n')
    valid_lines = []
    for line in lines:
        parts = line.split()
        if not parts: continue
        old_id = parts[0]
        new_id = KAG_TO_SILVER.get(old_id) if source == "kaggle" else ROBO_TO_SILVER.get(old_id)
        if new_id:
            parts[0] = new_id
            valid_lines.append(" ".join(parts))
    return "\n".join(valid_lines) if valid_lines else None

def copy_files_to_silver(partition):
    
    for row in partition:
            source, split, filename, content = row
            target_split = "val" if split in ["val", "valid"] else "train"
            prefix = "k_" if source == "kaggle" else "r_"
            img_name = filename.replace(".txt", ".jpg")
            folder_src = "plant-doc" if source == "kaggle" else "roboflow"
            src_img = os.path.join(BRONZE_DIR, folder_src, "images", split, img_name)
            dst_img = os.path.join(SILVER_DIR, target_split, "images", f"{prefix}{img_name}")
            dst_lbl = os.path.join(SILVER_DIR, target_split, "labels", f"{prefix}{filename}")
            
            if os.path.exists(src_img):
                shutil.copy(src_img, dst_img)
                with open(dst_lbl, "w") as f:
                    f.write(content)

def process_silver():
    
    if os.path.exists(SILVER_DIR): shutil.rmtree(SILVER_DIR)
    for s in ['train', 'val']:
        for d in ['images', 'labels']:
            os.makedirs(f"{SILVER_DIR}/{s}/{d}", exist_ok=True)

    # Kaggle
    kag_rdd = spark.sparkContext.wholeTextFiles(f"{BRONZE_DIR}/plant-doc/labels/*/*.txt") \
        .map(lambda x: ("kaggle", x[0].split('/')[-2], os.path.basename(x[0]), x[1]))
    
    # Roboflow
    robo_rdd = spark.sparkContext.wholeTextFiles(f"{BRONZE_DIR}/roboflow/labels/*/*.txt") \
        .map(lambda x: ("roboflow", x[0].split('/')[-2], os.path.basename(x[0]), x[1]))

    all_data_df = kag_rdd.union(robo_rdd).toDF(["source", "split", "filename", "raw_content"])

    map_udf = udf(filter_and_reindex_udf, StringType())
    silver_df = all_data_df.withColumn("content", map_udf(col("raw_content"), col("source"))) \
                           .filter(col("content").isNotNull()) \
                           .select("source", "split", "filename", "content")

    
    silver_df.rdd.foreachPartition(copy_files_to_silver)

    #  YAML 
    yaml_content = {
        'path': '/opt/airflow/data/silver',
        'train': 'train/images',
        'val': 'val/images',
        'nc': 18,
        'names': FINAL_NAMES
    }
    
    with open(os.path.join(SILVER_DIR, 'data.yaml'), 'w') as f:
        yaml.dump(yaml_content, f, default_flow_style=False)

    print(f"Couche Silver terminée. Total classes : 18. Fichiers fusionnés dans {SILVER_DIR}")

if __name__ == "__main__":
    process_silver()
