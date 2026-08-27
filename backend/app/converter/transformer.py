from typing import Any


class DataTransformer:
    """
    Se encarga de transformar los valores después
    del mapeo y antes de la validación.

    Las transformaciones se reciben mediante configuración.
    """

    def __init__(
        self,
        transformations: dict[str, Any] | None = None,
    ):
        self.transformations = transformations or {}

    def transform_value(
        self,
        value: Any,
        rules: Any = None,
    ) -> Any:
        """
        Aplica las reglas de transformación a un valor.
        """

        if value is None:
            return value

        # ---------------------------------------------
        # Compatibilidad: limpieza básica de strings
        # ---------------------------------------------

        if isinstance(value, str):
            value = value.strip()

        if not rules:
            return value

        # ---------------------------------------------
        # Reglas expresadas como lista
        # ---------------------------------------------

        if isinstance(rules, list):

            for rule in rules:

                if rule == "strip":
                    if isinstance(value, str):
                        value = value.strip()

                elif rule == "uppercase":
                    if isinstance(value, str):
                        value = value.upper()

                elif rule == "lowercase":
                    if isinstance(value, str):
                        value = value.lower()

            return value

        # ---------------------------------------------
        # Regla default
        # ---------------------------------------------

        if isinstance(rules, dict):

    # ---------------------------------------------
    # Valor por defecto
    # ---------------------------------------------

            if (
                rules.get("default") is not None
                and (
                    value is None
                    or value == ""
                )
            ):
                value = rules["default"]

            # ---------------------------------------------
            # Redondeo de números
            # ---------------------------------------------

            if rules.get("round") is not None:

                decimals = int(rules["round"])

                if isinstance(value, (int, float)):
                    value = round(value, decimals)

        return value

    def transform_row(
        self,
        row: dict[str, Any],
    ) -> dict[str, Any]:

        transformed_row = {}

        for key, value in row.items():

            rules = self.transformations.get(
                key
            )

            transformed_row[key] = self.transform_value(
                value,
                rules,
            )

        return transformed_row

    def transform_rows(
        self,
        rows: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        return [
            self.transform_row(row)
            for row in rows
        ]