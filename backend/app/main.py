from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.app.api.analyze import router as analyze_router
from backend.app.api.upload import router as upload_router
from backend.app.services.config_manager import ConfigManager


BASE_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = BASE_DIR / "frontend"

CLIENTS_CONFIG_DIR = BASE_DIR / "config" / "clients"

config_manager = ConfigManager(CLIENTS_CONFIG_DIR)


app = FastAPI(
    title="TÍO PABLO",
    description="Conversor de archivos Excel para CONTASOL",
    version="0.1.0",
)


app.include_router(upload_router)
app.include_router(analyze_router)


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "message": "TÍO PABLO funcionando correctamente",
    }


@app.get("/api/clients")
def get_clients():
    return {
        "clients": config_manager.list_clients()
    }


app.mount(
    "/",
    StaticFiles(directory=FRONTEND_DIR, html=True),
    name="frontend",
)