from fastapi import APIRouter, HTTPException

from backend.app.services.config_manager import ConfigManager


router = APIRouter(
    prefix="/api/clients",
    tags=["Clients"],
)


config_manager = ConfigManager(
    # Esta ruta se sustituirá posteriormente por la configuración
    # centralizada de la aplicación.
    __import__("pathlib").Path(__file__).resolve().parents[3]
    / "config"
    / "clients"
)


@router.get("/{client_id}/conversions")
def get_client_conversions(client_id: str):
    """Devuelve las conversiones disponibles para un cliente."""

    try:
        conversions = config_manager.list_conversions(client_id)

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"No existe el cliente: {client_id}",
        )

    return {
        "client": client_id,
        "conversions": conversions,
    }