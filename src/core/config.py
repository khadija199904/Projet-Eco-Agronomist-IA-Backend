from dotenv import load_dotenv
import os
import urllib.parse

# Load environment variables from .env
load_dotenv(override=True)

class Settings:
    PROJECT_NAME: str = "Eco Agronomist IA"
    PROJECT_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    
    # CORS & Security
    ALLOWED_ORIGINS: list = ["*"]  
    ALLOWED_HOSTS: list = ["*"]

    # Paths & Models
    PLANT_MODEL_PATH: str = os.getenv("PLANT_MODEL_PATH", "artifacts/plants/maladies_plant5_v1.pt")
    VALORISATION_MODEL_PATH: str = os.getenv("VALORISATION_MODEL_PATH", "artifacts/products/agrivision_anomaly_s_v1/agrivision_anomaly_s.pt")
    CONSUMER_MODEL_PATH: str = os.getenv("CONSUMER_MODEL_PATH", "artifacts/products/agrivision_consumer_last2_v1/agrivision_consumer_last2.pt")
    UPLOAD_DIR: str = "uploads/diagnostics"
    
    ONSSA_PDF1_PATH: str | None = os.getenv("ONSSA_PDF1_PATH")
    ONSSA_PDF2_PATH: str | None = os.getenv("ONSSA_PDF2_PATH")
    
    EMBEDDING_MODEL_NAME: str | None = os.getenv("EMBEDDING_MODEL_NAME")
    VECTOR_DB_DIR: str | None = os.getenv("VECTOR_DB_DIR")
    
    # AI Keys & Services
    GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY")
    PINECONE_API_KEY: str | None = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "eco-agronomist")
    
    # Supabase
    SUPABASE_URL: str | None = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: str | None = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
    
    # MLflow
    MLFLOW_TRACKING_URI: str = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
    MLFLOW_EXPERIMENT_NAME: str = os.getenv("MLFLOW_EXPERIMENT_NAME", "Diagnostic_Tracking")

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

# Global Exports for Compatibility
ONSSA_PDF1_PATH = settings.ONSSA_PDF1_PATH
ONSSA_PDF2_PATH = settings.ONSSA_PDF2_PATH
EMBEDDING_MODEL_NAME = settings.EMBEDDING_MODEL_NAME
VECTOR_DB_DIR = settings.VECTOR_DB_DIR
GROQ_API_KEY = settings.GROQ_API_KEY
PINECONE_API_KEY = settings.PINECONE_API_KEY
PINECONE_INDEX_NAME = settings.PINECONE_INDEX_NAME
SUPABASE_URL = settings.SUPABASE_URL
SUPABASE_KEY = settings.SUPABASE_KEY
PLANT_MODEL_PATH = settings.PLANT_MODEL_PATH
VALORISATION_MODEL_PATH = settings.VALORISATION_MODEL_PATH
CONSUMER_MODEL_PATH = settings.CONSUMER_MODEL_PATH
MLFLOW_TRACKING_URI = settings.MLFLOW_TRACKING_URI
MLFLOW_EXPERIMENT_NAME = settings.MLFLOW_EXPERIMENT_NAME
SECRET_KEY = settings.SECRET_KEY
DATABASE_URL = settings.DATABASE_URL

if __name__ == "__main__":
    from sqlalchemy import create_engine
    if DATABASE_URL:
        engine = create_engine(DATABASE_URL)
        try:
            with engine.connect() as connection:
                print("Connection successful!")
        except Exception as e:
            print(f"Failed to connect: {e}")
    else:
        print("DATABASE_URL not configured.")
