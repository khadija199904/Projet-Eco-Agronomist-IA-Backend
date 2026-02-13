from dotenv import load_dotenv
import os
# import chromadb

# Load environment variables from .env
load_dotenv()


PDF_PATH = os.getenv("DATA_PATH")

EMBEDDING_MODEL_NAME= os.getenv("EMBEDDING_MODEL_NAME")
VECTOR_DB_DIR = os.getenv("VECTOR_DB_DIR")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# 2 eme methode 
HF_TOKEN = os.getenv("HF_TOKEN")


# CHROMA CONFIGURATION
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = os.getenv("CHROMA_PORT", "9000")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "smartops_collection")

DATABASE_URL = os.getenv("DATABASE_URL")

SECRET_KEY = os.getenv("SECRET_KEY")
MLFLOW_TRACKING_URI =   os.getenv("MLFLOW_TRACKING_URI")

if not DATABASE_URL :
    # Fetch variables
     USER = os.getenv("POSTGRES_USER")
     PASSWORD = os.getenv("POSTGRES_PASSWORD")
     HOST = os.getenv("POSTGRES_HOST")
     PORT = os.getenv("POSTGRES_PORT")
     DBNAME = os.getenv("POSTGRES_DB")

     # Construct the SQLAlchemy connection string
     DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"


 # Configuration de JWT
SECRET_KEY = os.getenv("SECRET_KEY")






if __name__ == "__main__":
#   try:
#     client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT )
#     print(f"Connecté au serveur Chroma sur {CHROMA_HOST}:{CHROMA_PORT }")
#   except Exception as e:
#     print(f"Erreur de connexion : {e}")