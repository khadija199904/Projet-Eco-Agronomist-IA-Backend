from src.ai.rag.engine import ask_onssa_advisor, ask_onssa_ordonnance

async def query_rag(question: str) -> dict:
    """
    RÔLE : Interroge le moteur RAG en mode ADVISOR (Chat général).
    """
    try:
        result = ask_onssa(question)
        return result
    except Exception as e:
        return {"error": str(e)}

async def get_ordonnance(pathologies: list, culture: str = None) -> str:
    """
    RÔLE : Génère une ordonnance formelle via RAG pour une liste de pathologies.
    """
    if not pathologies:
        return "Aucune pathologie détectée."
    
    question = f"Génère une ordonnance pour traiter {', '.join(pathologies)} sur une culture de {culture or 'plante'}."
    try:
        result = ask_onssa_ordonnance(question)
        return result.get("answer", "Information non disponible.")
    except Exception as e:
        return f"Erreur lors de la génération de l'ordonnance : {str(e)}"
