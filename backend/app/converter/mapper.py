from typing import Any


class ExcelMapper:
    """
    Se encarga de mapear los datos del Excel de entrada
    al modelo interno que utilizará el conversor.

    Las reglas concretas de cada cliente se añadirán
    posteriormente mediante configuración.
    """

    def __init__(self, mapping: dict[str, str] | None = None):
        self.mapping = mapping or {}
        

    def map_row(self, row: dict[str, Any]) -> dict[str, Any]:
        if not self.mapping:
            return row.copy()

        mapped_row = {}

        for source_column, target_field in self.mapping.items():

            if source_column in row:
                mapped_row[target_field] = row[source_column]
            else:
                mapped_row[target_field] = None

        return mapped_row

    def map_rows(
        self,
        rows: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Mapea todas las filas del Excel.
        """

        return [
            self.map_row(row)
            for row in rows
        ]