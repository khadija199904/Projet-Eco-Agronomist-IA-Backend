from spark-session import get_spark_session
from spark-session import get_spark_session
import os

spark = get_spark_session("Silver_Layer_Processing")

# Liste des classes cibles pour Agadir
target_classes = ["Tomato", "Pepper", "Corn", "Potato"] # À adapter selon PlantDoc

def process_silver():
    # Dans le cas d'images, on filtre souvent les répertoires
    bronze_dir = "/data/bronze/plantdoc_raw/TRAIN"
    silver_dir = "/data/silver/filtered_images"
    
    target_plants = {
    "Poivron": ["poivron", "pepper", "bell pepper"],
    "Agrumes": ["agrumes", "citrus", "orange", "lemon", "citron", "mandarine", "clementine"],
    "Banane": ["banane", "banana"],
    "Haricot": ["haricot", "bean"],
    "Myrtille": ["myrtille", "blueberry"],
    "Mais": ["mais", "corn", "maize"],
    "Courgette": ["courgette", "zucchini", "squash"],
    "Aubergine": ["aubergine", "eggplant"]
}
    # On utilise Spark pour lister et filtrer si on a des métadonnées (CSV/JSON)
    # Sinon, on filtre par noms de dossiers
    for folder in os.listdir(bronze_dir):
        if any(crop in folder for crop in target_classes):
            print(f"Conservation de la classe : {folder}")
            # Logique de transfert Spark ou Shutil
            # ...
    print("Couche Silver prête.")

if __name__ == "__main__":
    process_silver()