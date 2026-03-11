from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from src.database.database import Base,engine
from src.api.v1 import routers
from src.api.v1.middleware.cors import setup_cors
from src.core.config import settings
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API intelligente de diagnostic phytosanitaire, valorisation post-récolte et traçabilité agricole",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

Base.metadata.create_all(bind=engine)


# setup_cors(app)

# app.add_middleware(
#     TrustedHostMiddleware,
#     allowed_hosts=settings.ALLOWED_HOSTS,
# )

PREFIX = settings.PROJECT_V1_STR

app.include_router(routers.auth,          prefix=f"{PREFIX}/auth",         tags=["Authentification"])
app.include_router(routers.organization,  prefix=f"{PREFIX}/organization", tags=["Organisations"])
app.include_router(routers.diagnostic,    prefix=f"{PREFIX}/diagnostic",   tags=["IA Diagnostic"])
app.include_router(routers.production,    prefix=f"{PREFIX}/production",   tags=["Production & Traçabilité Agricole"])
app.include_router(routers.valorisation,  prefix=f"{PREFIX}/valorisation", tags=["Valorisation - Traitement Station"])



