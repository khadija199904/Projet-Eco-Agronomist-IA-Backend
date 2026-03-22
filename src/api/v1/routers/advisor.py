from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.ai.rag.engine import ask_rag

router = APIRouter()

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: list[str]

@router.post("/query", response_model=QueryResponse)
async def ask_advisor(request: QueryRequest):
    """
    Endpoint RAG : Interroge le conseiller expert sur les documents agricoles.
    """
    if not request.question:
        raise HTTPException(status_code=400, detail="La question ne peut pas être vide.")
    
    # Appel de la fonction RAG
    result = ask_rag(request.question)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
        
    return QueryResponse(
        answer=result["answer"],
        sources=result["sources"]
    )
