from .auth import router as auth
from .diagnostic import router as diagnostic
from .lots import router as lots
from .valorisation import router as valorisation

__all__ = ["auth", "diagnostic", "lots", "valorisation"]
