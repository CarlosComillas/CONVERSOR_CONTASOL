import json
from pathlib import Path


class ConfigManager:
    """Gestiona las configuraciones de los clientes."""

    def __init__(self, config_directory: Path):
        self.config_directory = config_directory

    def list_clients(self) -> list[dict]:
        """Devuelve la información de los clientes configurados."""

        if not self.config_directory.exists():
            return []

        clients = []

        for config_file in sorted(self.config_directory.glob("*.json")):
            with config_file.open("r", encoding="utf-8") as file:
                config = json.load(file)

            clients.append(config)

        return clients

    def load_client(self, client_id: str) -> dict:
        """Carga la configuración de un cliente."""

        config_file = self.config_directory / f"{client_id}.json"

        if not config_file.exists():
            raise FileNotFoundError(
                f"No existe la configuración del cliente: {client_id}"
            )

        with config_file.open("r", encoding="utf-8") as file:
            return json.load(file)