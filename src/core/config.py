from dotenv import load_dotenv
import os
import urllib.parse

# import chromadb

# Load environment variables from .env
load_dotenv()


ONSSA_PDF_PATH = os.getenv("ONSSA_PDF_PATH")
RAP_PDF_PATH = os.getenv("RAP_PDF_PATH")
INRA_PDF_PATH = os.getenv("INRA_PDF_PATH")

EMBEDDING_MODEL_NAME= os.getenv("EMBEDDING_MODEL_NAME")
VECTOR_DB_DIR = os.getenv("VECTOR_DB_DIR")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
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
        USER = os.getenv("DB_USER").strip()
        PASSWORD = os.getenv("DB_PASSWORD").strip()
        HOST = os.getenv("DB_HOST").strip()
        PORT = os.getenv("DB_PORT").strip()
        DBNAME = os.getenv("DB_NAME").strip()
        encoded_password = urllib.parse.quote_plus(PASSWORD)
        DATABASE_URL = f"postgresql://{USER}:{encoded_password}@{HOST}:{PORT}/{DBNAME}?sslmode=require"



settings = Settings()

PLANT_MODEL_PATH = settings.PLANT_MODEL_PATH
VALORISATION_MODEL_PATH = settings.VALORISATION_MODEL_PATH
SECRET_KEY = settings.SECRET_KEY
DATABASE_URL = settings.DATABASE_URL


if __name__ == "__main__":
    from sqlalchemy import create_engine
    engine = create_engine(DATABASE_URL)
    try:
        with engine.connect() as connection:
            print("Connection successful!")
    except Exception as e:
        print(f"Failed to connect: {e}")
#   try:
#     client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT )
#     print(f"Connecté au serveur Chroma sur {CHROMA_HOST}:{CHROMA_PORT }")
#   except Exception as e:
#     print(f"Erreur de connexion : {e}")