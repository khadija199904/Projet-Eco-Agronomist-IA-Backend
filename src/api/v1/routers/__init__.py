from .auth import router as auth
from .diagnostic import router as diagnostic
from .production import router as production
from .valorisation import router as valorisation
from .organization import router as organization

__all__ = ["auth", "diagnostic", "production", "valorisation", "organization"]
