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
    # CONVERTIR A NÚMERO
    # =================================================

    def _to_number(
        self,
        value: Any,
    ) -> float:
        """
        Convierte un valor a número.

        Los valores vacíos o no numéricos se
        consideran 0 para las operaciones.
        """

        if value is None:
            return 0.0

        if isinstance(
            value,
            bool,
        ):
            return float(value)

        try:

            if isinstance(
                value,
                str,
            ):
                value = value.strip()

                if not value:
                    return 0.0

                # Permitir números escritos con coma decimal
                value = value.replace(
                    ",",
                    ".",
                )

            return float(value)

        except (
            TypeError,
            ValueError,
        ):

            return 0.0

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
            ],
            "output": "Salario total"
        }
        """

        operation_type = operation.get(
            "operation"
        )

        columns = operation.get(
            "columns",
            [],
        )

        if not columns:
            return None

        # ---------------------------------------------
        # Obtener valores
        # ---------------------------------------------

        values = [
            self._to_number(
                row.get(column)
            )
            for column in columns
        ]

        if not values:
            return None

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

        # ---------------------------------------------
        # Operación desconocida
        # ---------------------------------------------

        return None

    # =================================================
    # LIMPIAR RESULTADO NUMÉRICO
    # =================================================

    def clean_numeric_result(
        self,
        value: Any,
    ) -> Any:
        """
        Evita resultados como 10.0 cuando el resultado
        realmente es un número entero.
        """

        if (
            isinstance(value, float)
            and value.is_integer()
        ):
            return int(value)

        return value

    # =================================================
    # TRANSFORMAR FILA
    # =================================================

    def transform_row(
        self,
        row: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Aplica todas las transformaciones a una fila.
        """

        transformed_row = row.copy()

        # ---------------------------------------------
        # 1. Transformaciones de valores existentes
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
        # 2. Operaciones que crean columnas nuevas
        # ---------------------------------------------

        operations = self.transformations.get(
            "_operations",
            [],
        )

        if not isinstance(
            operations,
            list,
        ):
            operations = []

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

            result = self.calculate_operation(
                transformed_row,
                operation,
            )

            transformed_row[
                output_column
            ] = self.clean_numeric_result(
                result
            )

        return transformed_row

    # =================================================
    # TRANSFORMAR TODAS LAS FILAS
    # =================================================

    def transform_rows(
        self,
        rows: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Aplica las transformaciones a todas las filas.
        """

        return [
            self.transform_row(row)
            for row in rows
        ]