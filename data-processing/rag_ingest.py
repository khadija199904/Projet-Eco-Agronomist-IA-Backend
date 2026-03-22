import os
from supabase import create_client
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from src.core.config import SUPABASE_URL, SUPABASE_KEY  
from src.core.config import ONSSA_PDF_PATH, RAP_PDF_PATH, INRA_PDF_PATH

PDF_PATHS = [ONSSA_PDF_PATH, RAP_PDF_PATH, INRA_PDF_PATH]

# 1. Initialisation des clients
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2') 

def run_ingestion():
    # 2. Configuration du splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )

    all_data = []

    for path in PDF_PATHS:
        if not os.path.exists(path):
            print(f"Fichier non trouvé : {path}")
            continue
            
        print(f"Lecture de : {path}")
        loader = PyPDFLoader(path)
        pages = loader.load()
        chunks = text_splitter.split_documents(pages)

        for i, chunk in enumerate(chunks):
            # 3. Génération du vecteur (Embedding)
            print(f"  -> Vectorisation chunk {i}/{len(chunks)}...", end="\r")
            vector = model.encode(chunk.page_content).tolist()

            all_data.append({
                "content": chunk.page_content,
                "metadata": {"source": path, "page": chunk.metadata.get("page")},
                "embedding": vector
            })

    # 4. Envoi groupé vers Supabase
    if all_data:
        print(f" Envoi de {len(all_data)} chunks vers Supabase...")
        for i in range(0, len(all_data), 100):
            batch = all_data[i : i + 100]
            supabase.table("documents").insert(batch).execute()
        
        print("Terminé ! Tes PDF sont indexés.")

if __name__ == "__main__":
    run_ingestion()