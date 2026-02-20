from src.database.database import SessionLocal
from sqlalchemy.orm import Session


# Dépendance pour la base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
