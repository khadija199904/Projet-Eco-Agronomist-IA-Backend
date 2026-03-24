from fastapi.testclient import TestClient
from src.api.main import app
import os

client = TestClient(app)

def test_health_check_docs():
    """
    Test très simple : vérifie que la documentation Swagger est accessible.
    Cela garantit que l'application FastAPI démarre sans erreur de configuration.
    """
    response = client.get("/docs")
    assert response.status_code == 200

def test_project_settings():
    """
    Vérifie que le fichier de configuration charge bien le nom du projet.
    """
    from src.core.config import settings
    assert settings.PROJECT_NAME == "Eco Agronomist IA"

def test_uploads_directory():
    """
    Vérifie que le dossier uploads existe.
    """
    assert os.path.exists("uploads")
