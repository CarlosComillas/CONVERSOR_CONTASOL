import json
from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from backend.app.converter.excel_reader import ExcelReader
from backend.app.converter.excel_writer import ExcelWriter
from backend.app.converter.mapper import ExcelMapper
from backend.app.converter.transformer import DataTransformer
from backend.app.converter.validator import DataValidator
from backend.app.services.config_manager import ConfigManager


router = APIRouter(
    prefix="/api",
    tags=["Conversion"],
)


BASE_DIR = Path(__file__).resolve().parents[3]

INPUT_DIR = BASE_DIR / "data" / "input"
OUTPUT_DIR = BASE_DIR / "data" / "output"

CLIENTS_CONFIG_DIR = BASE_DIR / "config" / "clients"

config_manager = ConfigManager(CLIENTS_CONFIG_DIR)


# =================================================
# HELPERS
# =================================================

def parse_json_parameter(
    value: str | None,
    parameter_name: str,
):
    """
    Convierte un parámetro JSON recibido
    por query string en un objeto Python.
    """

    if value is None:
        return None

    try:
        return json.loads(value)

    except json.JSONDecodeError as error:

        raise HTTPException(
            status_code=400,
            detail=(
                f"El parámetro '{parameter_name}' "
                "no tiene un formato JSON válido."
            ),
        ) from error


def filter_selected_rows(
    dataframe: pd.DataFrame,
    selected_rows: list[int] | None,
    header_row: int,
) -> pd.DataFrame:
    """
    Conserva únicamente las filas seleccionadas.

    Los números recibidos son los números reales
    de fila del Excel.
    """

    if not selected_rows:
        return dataframe

    normalized_rows = set()

    for row_number in selected_rows:

        try:

            normalized_rows.add(
                int(row_number)
            )

        except (
            TypeError,
            ValueError,
        ):

            continue

    if not normalized_rows:
        return dataframe

    selected_indexes = []

    for index in dataframe.index:

        excel_row_number = (
            int(index)
            + header_row
            + 2
        )

        if excel_row_number in normalized_rows:

            selected_indexes.append(
                index
            )

    return dataframe.loc[
        selected_indexes
    ].copy()


# =================================================
# CONVERSIÓN
# =================================================

@router.post("/convert")
def convert_excel(
    filename: str,
    client_id: str,
    conversion_id: str,
    selected_columns: str | None = None,
    transformations: str | None = None,
    selected_rows: str | None = None,
):
    """
    Convierte un Excel.

    Permite seleccionar manualmente:

    - columnas
    - filas
    - transformaciones

    Si no se seleccionan filas,
    se conservan todas.
    """

    # =================================================
    # 1. CLIENTE
    # =================================================

    try:

        config_manager.load_client(
            client_id
        )

    except FileNotFoundError:

        raise HTTPException(
            status_code=404,
            detail=(
                f"No existe el cliente: "
                f"{client_id}"
            ),
        )

    # =================================================
    # 2. CONVERSIÓN
    # =================================================

    try:

        conversion = (
            config_manager.load_conversion(
                client_id,
                conversion_id,
            )
        )

    except FileNotFoundError:

        raise HTTPException(
            status_code=404,
            detail=(
                f"No existe la conversión "
                f"'{conversion_id}' para el "
                f"cliente '{client_id}'."
            ),
        )

    # =================================================
    # 3. ARCHIVO
    # =================================================

    input_path = (
        INPUT_DIR
        / Path(filename).name
    )

    if not input_path.exists():

        raise HTTPException(
            status_code=404,
            detail=(
                "No se encontró el "
                "archivo Excel."
            ),
        )

    if input_path.suffix.lower() not in {
        ".xlsx",
        ".xls",
    }:

        raise HTTPException(
            status_code=400,
            detail=(
                "El archivo debe ser un "
                "Excel .xlsx o .xls."
            ),
        )

    # =================================================
    # 4. SALIDA
    # =================================================

    output_filename = (
        f"CONTASOL_{client_id}_"
        f"{conversion_id}_"
        f"{input_path.stem}.xlsx"
    )

    output_path = (
        OUTPUT_DIR
        / output_filename
    )

    try:

        # =================================================
        # 5. CONFIGURACIÓN
        # =================================================

        mapping = conversion.get(
            "mapping",
            {},
        )

        configured_columns = (
            conversion.get(
                "selected_columns"
            )
        )

        validation_config = (
            conversion.get(
                "validation",
                {},
            )
        )

        required_fields = (
            validation_config.get(
                "required_fields",
                [],
            )
        )

        # =================================================
        # 6. COLUMNAS SELECCIONADAS
        # =================================================

        selected_columns_list = (
            parse_json_parameter(
                selected_columns,
                "selected_columns",
            )
        )

        if selected_columns_list is None:

            selected_columns_list = (
                configured_columns
            )

        if selected_columns_list is not None:

            if not isinstance(
                selected_columns_list,
                list,
            ):

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "La selección de columnas "
                        "debe ser una lista."
                    ),
                )

            if not all(
                isinstance(
                    column,
                    str,
                )
                for column
                in selected_columns_list
            ):

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Los nombres de las columnas "
                        "deben ser texto."
                    ),
                )

        # =================================================
        # 7. TRANSFORMACIONES
        # =================================================

        manual_transformations = (
            parse_json_parameter(
                transformations,
                "transformations",
            )
        )

        if manual_transformations is not None:

            if not isinstance(
                manual_transformations,
                list,
            ):

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Las transformaciones "
                        "deben ser una lista."
                    ),
                )

            transformations_config = {}

            for operation in (
                manual_transformations
            ):

                if not isinstance(
                    operation,
                    dict,
                ):

                    continue

                output = operation.get(
                    "output"
                )

                operation_type = (
                    operation.get(
                        "operation"
                    )
                )

                columns = operation.get(
                    "columns",
                    [],
                )

                if not output:

                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "Toda transformación "
                            "debe tener una columna "
                            "de salida."
                        ),
                    )

                if not isinstance(
                    columns,
                    list,
                ):

                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "Las columnas de una "
                            "transformación deben "
                            "ser una lista."
                        ),
                    )

                transformations_config.setdefault(
                    "_operations",
                    [],
                ).append(
                    {
                        "operation":
                            operation_type,

                        "columns":
                            columns,

                        "output":
                            output,
                    }
                )

        else:

            transformations_config = (
                conversion.get(
                    "transformations",
                    {},
                )
            )

        # =================================================
        # 8. FILAS SELECCIONADAS
        # =================================================

        selected_rows_config = (
            parse_json_parameter(
                selected_rows,
                "selected_rows",
            )
        )

        if selected_rows_config is not None:

            if not isinstance(
                selected_rows_config,
                dict,
            ):

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "La selección de filas "
                        "debe ser un objeto "
                        "por hoja."
                    ),
                )

        # =================================================
        # 9. LEER EXCEL
        # =================================================

        reader = ExcelReader(
            input_path
        )

        sheet_names = (
            reader.get_sheet_names()
        )

        if not sheet_names:

            raise HTTPException(
                status_code=400,
                detail=(
                    "El Excel no contiene "
                    "ninguna hoja."
                ),
            )

        # =================================================
        # 10. HOJA ACTUAL
        # =================================================

        sheet_name = sheet_names[0]

        dataframe = reader.read_sheet(
            sheet_name
        )

        header_row = (
            reader.detect_header_row(
                sheet_name
            )
        )

        # =================================================
        # 11. VALIDAR COLUMNAS
        # =================================================

        if selected_columns_list is not None:

            missing_columns = [
                column
                for column
                in selected_columns_list
                if column
                not in dataframe.columns
            ]

            if missing_columns:

                raise HTTPException(
                    status_code=400,
                    detail={
                        "message": (
                            "Algunas columnas "
                            "seleccionadas no "
                            "existen en el Excel."
                        ),
                        "missing_columns":
                            missing_columns,
                    },
                )

            dataframe = dataframe[
                selected_columns_list
            ].copy()

        # =================================================
        # 12. FILTRAR FILAS
        # =================================================

        rows_for_sheet = None

        if isinstance(
            selected_rows_config,
            dict,
        ):

            rows_for_sheet = (
                selected_rows_config.get(
                    sheet_name
                )
            )

        dataframe = filter_selected_rows(
            dataframe,
            rows_for_sheet,
            header_row,
        )

        # =================================================
        # 13. DATAFRAME → FILAS
        # =================================================

        rows = dataframe.to_dict(
            orient="records"
        )

        # =================================================
        # 14. MAPEAR
        # =================================================

        mapper = ExcelMapper(
            mapping=mapping,
            selected_columns=(
                selected_columns_list
            ),
        )

        mapped_rows = (
            mapper.map_rows(rows)
        )

        # =================================================
        # 15. TRANSFORMAR
        # =================================================

        transformer = DataTransformer(
            transformations=(
                transformations_config
            )
        )

        transformed_rows = (
            transformer.transform_rows(
                mapped_rows
            )
        )

        # =================================================
        # 16. VALIDAR
        # =================================================

        validator = DataValidator(
            required_fields=(
                required_fields
            )
        )

        validation_result = (
            validator.validate_rows(
                transformed_rows
            )
        )

        if not validation_result[
            "valid"
        ]:

            raise HTTPException(
                status_code=400,
                detail={
                    "message": (
                        "El Excel contiene "
                        "errores de validación."
                    ),
                    "validation":
                        validation_result,
                },
            )

        # =================================================
        # 17. ESCRIBIR
        # =================================================

        writer = ExcelWriter()

        writer.write(
            transformed_rows,
            output_path,
        )

    except HTTPException:

        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Error durante la conversión: "
                f"{error}"
            ),
        ) from error

    # =================================================
    # 18. DESCARGAR
    # =================================================

    return FileResponse(
        path=output_path,
        filename=output_filename,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )