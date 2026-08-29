import json
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from backend.app.converter.excel_reader import ExcelReader
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

config_manager = ConfigManager(
    CLIENTS_CONFIG_DIR
)


# =====================================================
# HELPERS
# =====================================================

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


# =====================================================
# NORMALIZAR CONFIGURACIÓN POR HOJA
# =====================================================

def normalize_sheet_configuration(
    configuration: Any,
    sheet_names: list[str],
    configuration_name: str,
) -> dict[str, Any]:
    """
    Normaliza una configuración que puede venir:

    - como lista, para mantener compatibilidad
      con versiones anteriores;
    - como diccionario por hoja.

    Ejemplo:

    {
        "Hoja 1": ["Nombre", "Importe"],
        "Hoja 2": ["Nombre", "DNI"]
    }
    """

    if configuration is None:

        return {
            sheet_name: None
            for sheet_name in sheet_names
        }

    if isinstance(
        configuration,
        list,
    ):

        return {
            sheet_name: configuration
            for sheet_name in sheet_names
        }

    if isinstance(
        configuration,
        dict,
    ):

        result = {}

        for sheet_name in sheet_names:

            result[sheet_name] = (
                configuration.get(
                    sheet_name
                )
            )

        return result

    raise HTTPException(
        status_code=400,
        detail=(
            f"El parámetro '{configuration_name}' "
            "debe ser una lista o un objeto "
            "por hoja."
        ),
    )


# =====================================================
# NORMALIZAR TRANSFORMACIONES
# =====================================================

def normalize_transformations(
    configuration: Any,
    sheet_names: list[str],
) -> dict[str, list[dict[str, Any]]]:
    """
    Normaliza las transformaciones para trabajar
    independientemente en cada hoja.

    Formato esperado:

    {
        "Hoja 1": [
            {
                "operation": "sum",
                "columns": ["A", "B"],
                "output": "Total"
            }
        ],
        "Hoja 2": []
    }

    También acepta una lista simple para mantener
    compatibilidad con la versión anterior.
    """

    if configuration is None:

        return {
            sheet_name: []
            for sheet_name in sheet_names
        }

    if isinstance(
        configuration,
        list,
    ):

        return {
            sheet_name: configuration
            for sheet_name in sheet_names
        }

    if isinstance(
        configuration,
        dict,
    ):

        result = {}

        for sheet_name in sheet_names:

            sheet_transformations = (
                configuration.get(
                    sheet_name,
                    []
                )
            )

            if sheet_transformations is None:

                sheet_transformations = []

            if not isinstance(
                sheet_transformations,
                list,
            ):

                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Las transformaciones "
                        f"de la hoja '{sheet_name}' "
                        "deben ser una lista."
                    ),
                )

            result[sheet_name] = (
                sheet_transformations
            )

        return result

    raise HTTPException(
        status_code=400,
        detail=(
            "El parámetro 'transformations' "
            "debe ser una lista o un objeto "
            "por hoja."
        ),
    )


# =====================================================
# FILTRAR FILAS
# =====================================================

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

        if (
            excel_row_number
            in normalized_rows
        ):

            selected_indexes.append(
                index
            )

    return dataframe.loc[
        selected_indexes
    ].copy()


# =====================================================
# CREAR CONFIGURACIÓN DE TRANSFORMACIONES
# =====================================================

def build_transformations_config(
    transformations: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Convierte las transformaciones enviadas desde
    el frontend al formato esperado por DataTransformer.
    """

    transformations_config: dict[
        str,
        Any
    ] = {}

    operations = []

    for operation in transformations:

        if not isinstance(
            operation,
            dict,
        ):

            continue

        output = operation.get(
            "output"
        )

        operation_type = operation.get(
            "operation"
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

        operations.append(
            {
                "operation":
                    operation_type,

                "columns":
                    columns,

                "output":
                    output,
            }
        )

    transformations_config[
        "_operations"
    ] = operations

    return transformations_config


# =====================================================
# CONVERSIÓN
# =====================================================

@router.post("/convert")
def convert_excel(
    filename: str,
    client_id: str,
    conversion_id: str,
    selected_columns: str | None = None,
    transformations: str | None = None,
    selected_rows: str | None = None,
    removed_columns: str | None = None,
):
    """
    Convierte un Excel.

    Permite seleccionar manualmente:

    - columnas
    - filas
    - transformaciones

    La selección puede realizarse de forma
    independiente para cada hoja.
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

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

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
        # 6. LEER EXCEL
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
        # 7. COLUMNAS SELECCIONADAS
        # =================================================

        selected_columns_config = (
            parse_json_parameter(
                selected_columns,
                "selected_columns",
            )
        )

        if (
            selected_columns_config
            is None
        ):

            selected_columns_config = (
                configured_columns
            )

        selected_columns_by_sheet = (
            normalize_sheet_configuration(
                selected_columns_config,
                sheet_names,
                "selected_columns",
            )
        )


        # =================================================
        # 8. COLUMNAS ELIMINADAS
        # =================================================

        removed_columns_config = (
            parse_json_parameter(
                removed_columns,
                "removed_columns",
            )
        )

        removed_columns_by_sheet = (
            normalize_sheet_configuration(
                removed_columns_config,
                sheet_names,
                "removed_columns",
            )
        )


        # =================================================
        # 9. TRANSFORMACIONES
        # =================================================

        manual_transformations = (
            parse_json_parameter(
                transformations,
                "transformations",
            )
        )

        if (
            manual_transformations
            is not None
        ):

            transformations_by_sheet = (
                normalize_transformations(
                    manual_transformations,
                    sheet_names,
                )
            )

        else:

            configured_transformations = (
                conversion.get(
                    "transformations",
                    {},
                )
            )

            transformations_by_sheet = (
                normalize_transformations(
                    configured_transformations,
                    sheet_names,
                )
            )


        # =================================================
        # 10. FILAS SELECCIONADAS
        # =================================================

        selected_rows_config = (
            parse_json_parameter(
                selected_rows,
                "selected_rows",
            )
        )

        if (
            selected_rows_config
            is not None
        ):

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
        # 11. PROCESAR TODAS LAS HOJAS
        # =================================================

        output_sheets = {}


        for sheet_name in sheet_names:

            # =================================================
            # LEER HOJA
            # =================================================

            dataframe = reader.read_sheet(
                sheet_name
            )

            header_row = (
                reader.detect_header_row(
                    sheet_name
                )
            )


            # =================================================
            # COLUMNAS DISPONIBLES
            # =================================================

            available_columns = [
                str(column)
                for column
                in dataframe.columns
            ]


            # =================================================
            # COLUMNAS ELIMINADAS
            # =================================================

            sheet_removed_columns = (
                removed_columns_by_sheet.get(
                    sheet_name
                )
            )

            if (
                sheet_removed_columns
                is None
            ):

                sheet_removed_columns = []


            if not isinstance(
                sheet_removed_columns,
                list,
            ):

                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Las columnas eliminadas "
                        f"de la hoja '{sheet_name}' "
                        "deben ser una lista."
                    ),
                )


            dataframe = dataframe.drop(
                columns=[
                    column
                    for column
                    in sheet_removed_columns
                    if column
                    in dataframe.columns
                ],
                errors="ignore",
            )


            # =================================================
            # COLUMNAS SELECCIONADAS
            # =================================================

            sheet_selected_columns = (
                selected_columns_by_sheet.get(
                    sheet_name
                )
            )


            if (
                sheet_selected_columns
                is not None
            ):

                if not isinstance(
                    sheet_selected_columns,
                    list,
                ):

                    raise HTTPException(
                        status_code=400,
                        detail=(
                            f"La selección de "
                            f"columnas de la hoja "
                            f"'{sheet_name}' debe "
                            "ser una lista."
                        ),
                    )


                if not all(
                    isinstance(
                        column,
                        str,
                    )
                    for column
                    in sheet_selected_columns
                ):

                    raise HTTPException(
                        status_code=400,
                        detail=(
                            f"Los nombres de las "
                            f"columnas de la hoja "
                            f"'{sheet_name}' deben "
                            "ser texto."
                        ),
                    )


                missing_columns = [
                    column
                    for column
                    in sheet_selected_columns
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
                            "sheet":
                                sheet_name,
                            "missing_columns":
                                missing_columns,
                        },
                    )


                dataframe = dataframe[
                    sheet_selected_columns
                ].copy()


            # =================================================
            # FILAS SELECCIONADAS
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
            # DATAFRAME → FILAS
            # =================================================

            rows = dataframe.to_dict(
                orient="records"
            )


            # =================================================
            # MAPEAR
            # =================================================

            mapper = ExcelMapper(
                mapping=mapping,
                selected_columns=(
                    sheet_selected_columns
                ),
            )

            mapped_rows = (
                mapper.map_rows(
                    rows
                )
            )


            # =================================================
            # TRANSFORMAR
            # =================================================

            sheet_transformations = (
                transformations_by_sheet.get(
                    sheet_name,
                    [],
                )
            )

            transformations_config = (
                build_transformations_config(
                    sheet_transformations
                )
            )

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
            # VALIDAR
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
                        "sheet":
                            sheet_name,
                        "validation":
                            validation_result,
                    },
                )


            # =================================================
            # GUARDAR RESULTADO DE LA HOJA
            # =================================================

            output_sheets[
                sheet_name
            ] = transformed_rows


        # =================================================
        # 12. ESCRIBIR TODAS LAS HOJAS
        # =================================================
        #
        # No utilizamos ExcelWriter.write() porque la
        # versión actual de ExcelWriter recibe una única
        # lista de filas y por tanto solo puede generar
        # una hoja.
        #
        # Aquí utilizamos pandas.ExcelWriter directamente
        # para conservar todas las hojas.
        # =================================================

        with pd.ExcelWriter(
            output_path,
            engine="openpyxl",
        ) as excel_writer:

            for (
                sheet_name,
                rows,
            ) in output_sheets.items():

                output_dataframe = (
                    pd.DataFrame(
                        rows
                    )
                )

                output_dataframe.to_excel(
                    excel_writer,
                    sheet_name=(
                        sheet_name[:31]
                    ),
                    index=False,
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
    # 13. DESCARGAR
    # =================================================

    return FileResponse(
        path=output_path,
        filename=output_filename,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )