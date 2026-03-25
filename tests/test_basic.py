from fastapi.testclient import TestClient
from src.api.main import app
import os

client = TestClient(app)

def test_health_check_docs():
    response = client.get("/docs")
    assert response.status_code == 200

def test_project_settings():
    
    from src.core.config import settings
    assert settings.PROJECT_NAME == "Eco Agronomist IA"

def test_uploads_directory():
    assert os.path.exists("uploads")
