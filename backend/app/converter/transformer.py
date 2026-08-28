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

    # =================================================
    # TRANSFORMACIONES DE VALORES INDIVIDUALES
    # =================================================

    def transform_value(
        self,
        value: Any,
        rules: Any = None,
    ) -> Any:
        """
        Aplica reglas de transformación a un valor.
        """

        if value is None:
            return value

        # ---------------------------------------------
        # Limpieza básica de strings
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
        # Reglas expresadas como diccionario
        # ---------------------------------------------

        if isinstance(rules, dict):

            # -----------------------------------------
            # Valor por defecto
            # -----------------------------------------

            if (
                rules.get("default") is not None
                and (
                    value is None
                    or value == ""
                )
            ):
                value = rules["default"]

            # -----------------------------------------
            # Redondeo
            # -----------------------------------------

            if rules.get("round") is not None:

                decimals = int(
                    rules["round"]
                )

                if isinstance(
                    value,
                    (int, float),
                ):
                    value = round(
                        value,
                        decimals,
                    )

        return value

    # =================================================
    # OPERACIONES NUMÉRICAS
    # =================================================

    def calculate_operation(
        self,
        row: dict[str, Any],
        operation: dict[str, Any],
    ) -> Any:
        """
        Realiza una operación matemática utilizando
        varias columnas de una fila.

        Ejemplo:

        {
            "operation": "sum",
            "columns": [
                "Salario",
                "Complemento"
            ]
        }
        """

        operation_type = operation.get(
            "operation"
        )

        columns = operation.get(
            "columns",
            []
        )

        if not columns:
            return None

        values = []

        for column in columns:

            value = row.get(
                column
            )

            if value is None:
                value = 0

            try:
                value = float(value)

            except (
                TypeError,
                ValueError,
            ):
                value = 0

            values.append(value)

        # ---------------------------------------------
        # SUMA
        # ---------------------------------------------

        if operation_type == "sum":

            return sum(values)

        # ---------------------------------------------
        # RESTA
        # ---------------------------------------------

        if operation_type == "subtract":

            result = values[0]

            for value in values[1:]:
                result -= value

            return result

        # ---------------------------------------------
        # MULTIPLICACIÓN
        # ---------------------------------------------

        if operation_type == "multiply":

            result = values[0]

            for value in values[1:]:
                result *= value

            return result

        # ---------------------------------------------
        # DIVISIÓN
        # ---------------------------------------------

        if operation_type == "divide":

            result = values[0]

            for value in values[1:]:

                if value == 0:
                    return None

                result /= value

            return result

        return None

    # =================================================
    # TRANSFORMAR FILA
    # =================================================

    def transform_row(
        self,
        row: dict[str, Any],
    ) -> dict[str, Any]:

        transformed_row = row.copy()

        # ---------------------------------------------
        # Transformaciones de valores existentes
        # ---------------------------------------------

        for key, value in row.items():

            rules = self.transformations.get(
                key
            )

            transformed_row[key] = (
                self.transform_value(
                    value,
                    rules,
                )
            )

        # ---------------------------------------------
        # Operaciones que crean nuevas columnas
        # ---------------------------------------------

        operations = self.transformations.get(
            "_operations",
            []
        )

        for operation in operations:

            if not isinstance(
                operation,
                dict,
            ):
                continue

            output_column = operation.get(
                "output"
            )

            if not output_column:
                continue

            transformed_row[
                output_column
            ] = self.calculate_operation(
                transformed_row,
                operation,
            )

        return transformed_row

    # =================================================
    # TRANSFORMAR TODAS LAS FILAS
    # =================================================

    def transform_rows(
        self,
        rows: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        return [
            self.transform_row(row)
            for row in rows
        ]