from typing import Any


class ExcelMapper:
    """
    Mapea y filtra los datos del Excel de entrada.

    - selected_columns: columnas que queremos conservar.
    - mapping: nombre de la columna de entrada -> nombre del campo final.
    """

    def __init__(
        self,
        mapping: dict[str, str] | None = None,
        selected_columns: list[str] | None = None,
    ):
        self.mapping = mapping or {}
        self.selected_columns = selected_columns

    def map_row(self,row: dict[str, Any],) -> dict[str, Any]:
        """
        Selecciona y mapea una fila.
        """

        # ---------------------------------------------
        # 1. Seleccionar columnas
        # ---------------------------------------------

        if self.selected_columns is not None:

            filtered_row = {
                column: row[column]
                for column in self.selected_columns
                if column in row
            }

        else:
            filtered_row = row.copy()

        # ---------------------------------------------
        # 2. Aplicar mapping
        # ---------------------------------------------

        if not self.mapping:
            return filtered_row

        mapped_row = {}

        for source_column, target_field in self.mapping.items():

            if source_column in filtered_row:
                mapped_row[target_field] = (
                    filtered_row[source_column]
                )

        return mapped_row

    def map_rows(
        self,
        rows: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Selecciona y mapea todas las filas.
        """

        return [
            self.map_row(row)
            for row in rows
        ]