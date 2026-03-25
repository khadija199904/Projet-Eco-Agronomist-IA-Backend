import pytest
from unittest.mock import MagicMock, patch
from src.api.v1.crud.diagnostic_crud import get_plant_diagnostic_by_id
from src.database.models.diagnostics_table import UniversalDiagnostic
from src.database.models.enums import DiagnosticType



def test_get_plant_diagnostic_mocked():
    
    mock_db = MagicMock()
    
    
    fake_diag = UniversalDiagnostic(id=1, diag_type=DiagnosticType.PLANT)
    
  
    mock_db.get.return_value = fake_diag
    
   
    result = get_plant_diagnostic_by_id(mock_db, 1)
    
    
    assert result is not None
    assert result.id == 1
    assert result.diag_type == DiagnosticType.PLANT
    mock_db.get.assert_called_once_with(UniversalDiagnostic, 1)



@pytest.mark.anyio
@patch("src.api.v1.services.rag_service.ask_onssa")
async def test_rag_service_simple_mock(mock_ask):
   
    from src.api.v1.services.rag_service import get_ordonnance
     
    mock_ask.return_value = {"answer": "Voici une ordonnance de test."}
    
   
    result = await get_ordonnance(["Ma plante a des taches"], "Tomate")
    
    
    assert "ordonnance de test" in result
    mock_ask.assert_called_once()
