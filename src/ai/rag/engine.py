from pinecone import Pinecone
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from src.core.config import GROQ_API_KEY, PINECONE_API_KEY, PINECONE_INDEX_NAME

# ── Init ─────────────────────────────────────────────────────────────────────
embeddings = HuggingFaceEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, groq_api_key=GROQ_API_KEY)

def _retrieve(question: str, k: int = 6) -> list[Document]:
    """Embed the question and query Pinecone directly (no langchain-pinecone needed)."""
    vector = embeddings.embed_query(question)
    results = index.query(vector=vector, top_k=k, include_metadata=True)
    return [
        Document(
            page_content=m.metadata.get("text", ""),
            metadata={"source": m.metadata.get("source", "?"), "id": m.id}
        )
        for m in results.matches
    ]


# ── Prompts ──────────────────────────────────────────────────────────────────

ADVISOR_PROMPT = PromptTemplate.from_template("""Tu es un expert agronome assistant pour les agriculteurs.
Réponds de manière informative et professionnelle en te basant UNIQUEMENT sur le contexte fourni.
Si l'information n'est pas dans le contexte, dis: "Je ne trouve pas l'information spécifique dans mes documents."

Contexte : {context}
Question : {question}
Réponse :""")

ORDONNANCE_PROMPT = PromptTemplate.from_template("""Tu es un conseiller agronomique ONSSA Maroc.
Réponds UNIQUEMENT depuis le contexte. Si absent : "Information non disponible."

Génère une ordonnance avec ce format — les CONSEILS apparaissent UNE SEULE FOIS à la fin :

============================
  ORDONNANCE PHYTOSANITAIRE
============================
Culture  : ...
Maladie  : ...
----------------------------
N°1. NOM_PRODUIT (formulation)
  Dose : ...  |  DAR : ... jours
  Matière active : ...

N°2. NOM_PRODUIT (formulation)
  Dose : ...  |  DAR : ... jours
  Matière active : ...
----------------------------
CONSEILS GÉNÉRAUX :
- Respecter le DAR.
- Porter gants et masque.
- Ne pas traiter par vent ou chaleur.
============================

Contexte : {context}
Question : {question}
Ordonnance :""")

# ── Chains ───────────────────────────────────────────────────────────────────

def _build_chain(prompt_template):
    def _context_fn(question: str) -> str:
        docs = _retrieve(question)
        return "\n\n".join(d.page_content for d in docs)
    
    return (
        {"context": RunnablePassthrough() | _context_fn,
         "question": RunnablePassthrough()}
        | prompt_template | llm | StrOutputParser()
    )

advisor_chain = _build_chain(ADVISOR_PROMPT)
ordonnance_chain = _build_chain(ORDONNANCE_PROMPT)

# ── Exported Functions ───────────────────────────────────────────────────────

def ask_onssa(question: str) -> dict:
    """Pour les prescriptions (Diagnostic)."""
    docs = _retrieve(question)
    return {
        "answer": ordonnance_chain.invoke(question),
        "sources": list({d.metadata.get("source", "?") for d in docs})
    }


if __name__ == "__main__":
    print("\n--- Test ORDONNANCE ---")
    print(ask_onssa("Traitements contre le mildiou sur tomate ?")["answer"])
