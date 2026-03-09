from dotenv import load_dotenv
import os
import urllib.parse
# import chromadb

# Load environment variables from .env
load_dotenv()


PDF_PATH = os.getenv("DATA_PATH")

EMBEDDING_MODEL_NAME= os.getenv("EMBEDDING_MODEL_NAME")
VECTOR_DB_DIR = os.getenv("VECTOR_DB_DIR")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class Settings:
    PROJECT_NAME: str = "Eco Agronomist IA"
    PROJECT_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    

    # CORS & Security
    ALLOWED_ORIGINS: list = ["*"]  
    ALLOWED_HOSTS: list = ["*"]

    # Paths
    PLANT_MODEL_PATH: str = os.getenv("PLANT_MODEL_PATH", "artifacts/plants/maladies_plant5_v1.pt")
    VALORISATION_MODEL_PATH: str = os.getenv("VALORISATION_MODEL_PATH", "artifacts/valorisation/qualite_v1.pt")
    UPLOAD_DIR: str = "uploads/diagnostics"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        USER = os.getenv("DB_USER", "postgres")
        PASSWORD = os.getenv("DB_PASSWORD", "")
        HOST = os.getenv("DB_HOST", "localhost")
        PORT = os.getenv("DB_PORT", "5432")
        DBNAME = os.getenv("DB_NAME", "eco_agri")
        encoded_password = urllib.parse.quote_plus(PASSWORD)
        DATABASE_URL = f"postgresql+psycopg2://{USER}:{encoded_password}@{HOST}:{PORT}/{DBNAME}"

settings = Settings()

PLANT_MODEL_PATH = settings.PLANT_MODEL_PATH
VALORISATION_MODEL_PATH = settings.VALORISATION_MODEL_PATH
SECRET_KEY = settings.SECRET_KEY
DATABASE_URL = settings.DATABASE_URL


# if __name__ == "__main__":
#   try:
#     client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT )
#     print(f"Connecté au serveur Chroma sur {CHROMA_HOST}:{CHROMA_PORT }")
#   except Exception as e:
#     print(f"Erreur de connexion : {e}")