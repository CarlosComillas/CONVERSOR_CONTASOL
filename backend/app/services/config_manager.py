import json
from pathlib import Path
from typing import Any


class ConfigManager:
    """Gestiona las configuraciones de clientes y sus conversiones."""

    def __init__(self, config_directory: Path):
        self.config_directory = config_directory

    def list_clients(self) -> list[dict[str, Any]]:
        """Devuelve la información de todos los clientes configurados."""

        if not self.config_directory.exists():
            return []

        clients = []

        for config_file in sorted(
            self.config_directory.glob("*.json")
        ):
            with config_file.open("r", encoding="utf-8") as file:
                config = json.load(file)

            clients.append(config)

        return clients

    def load_client(
        self,
        client_id: str
    ) -> dict[str, Any]:
        """Carga la configuración completa de un cliente."""

        config_file = self.config_directory / f"{client_id}.json"

        if not config_file.exists():
            raise FileNotFoundError(
                f"No existe la configuración del cliente: {client_id}"
            )

        with config_file.open("r", encoding="utf-8") as file:
            return json.load(file)

    def list_conversions(
        self,
        client_id: str
    ) -> list[dict[str, Any]]:
        """Devuelve las conversiones disponibles para un cliente."""

        client = self.load_client(client_id)

        return client.get("conversions", [])

    def load_conversion(
        self,
        client_id: str,
        conversion_id: str
    ) -> dict[str, Any]:
        """Carga una conversión concreta de un cliente."""

        conversions = self.list_conversions(client_id)

        for conversion in conversions:
            if conversion.get("id") == conversion_id:
                return conversion

        raise FileNotFoundError(
            f"No existe la conversión '{conversion_id}' "
            f"para el cliente '{client_id}'."
        )