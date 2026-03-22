from supabase.client import create_client
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from src.core.config import SUPABASE_URL, SUPABASE_KEY, GROQ_API_KEY

# 1. Initialisation globale (Une seule fois au démarrage)
embeddings = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

vector_store = SupabaseVectorStore(
    client=supabase,
    embedding=embeddings,
    table_name="documents",
    query_name="match_documents",
)

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, groq_api_key=GROQ_API_KEY)

# 2. Configuration du Prompt et de la Chaîne
prompt = PromptTemplate.from_template("""Tu es un expert agronome assistant.
Utilise UNIQUEMENT le contexte suivant pour répondre. Si tu ne sais pas, dis: 'Je ne trouve pas l'information'.

Contexte: {context}
Question: {question}
Réponse:""")

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vector_store.as_retriever(search_kwargs={"k": 5}),
    return_source_documents=True,
    chain_type_kwargs={"prompt": prompt}
)

def ask_rag(question: str):
    """Fonction simplifiée pour interroger le RAG."""
    try:
        result = qa_chain.invoke({"query": question})
        sources = list(set([doc.metadata.get("source", "Inconnue") for doc in result["source_documents"]]))
        return {"answer": result["result"], "sources": sources}
    except Exception as e:
        return {"error": f"Erreur RAG : {str(e)}"}

if __name__ == "__main__":
    # Test simple du moteur RAG
    query = "Comment traiter la mouche mildiou ?"
    print(f"\n--- Test Question: {query} ---")
    
    response = ask_rag(query)
    
    if "error" in response:
        print(f"Erreur : {response['error']}")
    else:
        print(f"Réponse : {response['answer']}")
        print(f"Sources : {response['sources']}")
