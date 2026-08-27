from typing import Any


class DataValidator:
    """
    Valida los datos antes de generar el Excel final.
    """

    def __init__(
        self,
        required_fields: list[str] | None = None
    ):
        self.required_fields = required_fields or []

    def validate_row(
        self,
        row: dict[str, Any]
    ) -> list[str]:

        errors = []

        for field in self.required_fields:

            if field not in row:
                errors.append(
                    f"Falta el campo obligatorio: {field}"
                )
                continue

            if row[field] is None:
                errors.append(
                    f"El campo obligatorio está vacío: {field}"
                )

        return errors

    def validate_rows(
        self,
        rows: list[dict[str, Any]]
    ) -> dict[str, Any]:

        errors = []

        for index, row in enumerate(rows, start=1):

            row_errors = self.validate_row(row)

            for error in row_errors:
                errors.append(
                    f"Fila {index}: {error}"
                )

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "total_rows": len(rows),
        }