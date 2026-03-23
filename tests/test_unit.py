import pytest
from unittest.mock import MagicMock, patch
from src.api.v1.crud.diagnostic_crud import get_plant_diagnostic_by_id
from src.database.models.diagnostics_table import UniversalDiagnostic
from src.database.models.enums import DiagnosticType

# --- 1. TEST AVEC MOCK DE LA BASE DE DONNÉES ---

def test_get_plant_diagnostic_mocked():
    """
    Test unitaire simple qui simule la base de données.
    On vérifie que la fonction CRUD appelle bien 'db.get' et retourne le bon objet.
    """
    # On crée une fausse session de base de données
    mock_db = MagicMock()
    
    # On crée un faux diagnostic que la DB est censée retourner
    fake_diag = UniversalDiagnostic(id=1, diag_type=DiagnosticType.PLANT)
    
    # On configure le mock pour retourner ce faux diagnostic quand on appelle db.get
    mock_db.get.return_value = fake_diag
    
    # Appel de la fonction à tester
    result = get_plant_diagnostic_by_id(mock_db, 1)
    
    # Vérifications
    assert result is not None
    assert result.id == 1
    assert result.diag_type == DiagnosticType.PLANT
    mock_db.get.assert_called_once_with(UniversalDiagnostic, 1)


# --- 2. TEST AVEC MOCK D'UN SERVICE IA ---

@patch("src.api.v1.services.rag_service.ask_onssa")
def test_rag_service_simple_mock(mock_ask):
    """
    Test qui simule l'appel au moteur RAG.
    On ne veut pas appeler l'IA (Groq/Pinecone) pendant les tests.
    """
    from src.api.v1.services.rag_service import generate_treatment_suggestion
    
    # On définit ce que l'IA est censée répondre
    mock_ask.return_value = "Voici une ordonnance de test."
    
    # On appelle notre service
    result = generate_treatment_suggestion("Ma plante a des taches", "Tomate")
    
    # On vérifie que le résultat est bien celui du mock
    assert "ordonnance de test" in result
    mock_ask.assert_called_once()
