"""Ponto de entrada da aplicação FastAPI."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import get_settings
from app.database import engine
from app.routers import (
    auth,
    dashboard,
    especialidades,
    externos,
    intermediarios,
    trabalhos,
)

settings = get_settings()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(especialidades.router)
app.include_router(intermediarios.router)
app.include_router(externos.router)
app.include_router(trabalhos.router)
app.include_router(dashboard.router)


@app.get("/health")
def health() -> dict:
    """Verifica que a app está viva e consegue falar com a base de dados."""
    db_ok = True
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        db_ok = False

    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.environment,
        "database": "ok" if db_ok else "unavailable",
    }
