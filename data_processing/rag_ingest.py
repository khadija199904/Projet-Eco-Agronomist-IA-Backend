import os
import re
import uuid
import pdfplumber
from pinecone import Pinecone
from langchain_huggingface import HuggingFaceEmbeddings
from src.core.config import PINECONE_API_KEY, PINECONE_INDEX_NAME, ONSSA_PDF1_PATH, ONSSA_PDF2_PATH

# ── Config ───────────────────────────────────────────────────────────────────
PDF_PATHS = [ONSSA_PDF1_PATH, ONSSA_PDF2_PATH]

embeddings = HuggingFaceEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)


def extract_text(path: str) -> str:
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text


def split_fiches(text: str) -> list:
    """Chaque fiche FICHE_TRAITEMENT devient un chunk."""
    parts = re.split(r"-*FICHE_TRAITEMENT:", text)
    return [
        "FICHE_TRAITEMENT: " + p.strip()
        for p in parts
        if len(p.strip()) > 50
    ]


def run_ingestion():
    all_vectors = []

    for path in PDF_PATHS:
        if not path or not os.path.exists(path):
            print(f"Ignoré : {path}")
            continue

        print(f"Lecture : {path}")
        fiches = split_fiches(extract_text(path))
        print(f"  {len(fiches)} fiches trouvées")

        for i, fiche in enumerate(fiches):
            print(f"  Embedding {i+1}/{len(fiches)}...", end="\r")
            all_vectors.append({
                "id": str(uuid.uuid4()),
                "values": embeddings.embed_query(fiche),
                "metadata": {
                    "text": fiche[:2000],
                    "source": os.path.basename(path),
                }
            })

    if all_vectors:
        print(f"\nEnvoi de {len(all_vectors)} vecteurs vers Pinecone...")
        for i in range(0, len(all_vectors), 100):
            index.upsert(vectors=all_vectors[i:i+100])
        print("Indexation terminée.")


if __name__ == "__main__":
    run_ingestion()