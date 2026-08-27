from typing import Any


class DataTransformer:
    """
    Se encarga de transformar los valores después
    del mapeo y antes de la validación.
    """

    def transform_value(self, value: Any) -> Any:
        """
        Punto central para las transformaciones.

        Las reglas concretas se añadirán cuando
        conozcamos el formato real de los archivos.
        """

        if isinstance(value, str):
            return value.strip()

        return value

    def transform_row(
        self,
        row: dict[str, Any]
    ) -> dict[str, Any]:

        return {
            key: self.transform_value(value)
            for key, value in row.items()
        }

    def transform_rows(
        self,
        rows: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:

        return [
            self.transform_row(row)
            for row in rows
        ]