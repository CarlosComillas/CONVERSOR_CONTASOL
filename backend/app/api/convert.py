import json
from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

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

config_manager = ConfigManager(
    CLIENTS_CONFIG_DIR
)


@router.post("/convert")
def convert_excel(
    filename: str,
    client_id: str,
    conversion_id: str,
    selected_columns: str | None = None,
    transformations: str | None = None,
):
    """
    Convierte un Excel utilizando la configuración
    del cliente y de la conversión seleccionada.

    La selección manual de columnas y las
    transformaciones creadas desde la interfaz
    tienen prioridad sobre las configuradas.
    """

    # =================================================
    # 1. COMPROBAR CLIENTE
    # =================================================

    try:

        config_manager.load_client(
            client_id
        )

    except FileNotFoundError:

        raise HTTPException(
            status_code=404,
            detail=f"No existe el cliente: {client_id}",
        )

    # =================================================
    # 2. CARGAR CONVERSIÓN
    # =================================================

    try:

        conversion = config_manager.load_conversion(
            client_id,
            conversion_id,
        )

    except FileNotFoundError:

        raise HTTPException(
            status_code=404,
            detail=(
                f"No existe la conversión "
                f"'{conversion_id}' para el cliente "
                f"'{client_id}'."
            ),
        )

    # =================================================
    # 3. COMPROBAR EXCEL
    # =================================================

    input_path = INPUT_DIR / filename

    if not input_path.exists():

        raise HTTPException(
            status_code=404,
            detail="No se encontró el archivo Excel.",
        )

    if input_path.suffix.lower() not in {
        ".xlsx",
        ".xls",
    }:

        raise HTTPException(
            status_code=400,
            detail=(
                "El archivo debe ser un Excel .xlsx o .xls."
            ),
        )

    # =================================================
    # 4. NOMBRE DEL ARCHIVO DE SALIDA
    # =================================================

    output_filename = (
        f"CONTASOL_{client_id}_{conversion_id}_"
        f"{input_path.stem}.xlsx"
    )

    output_path = OUTPUT_DIR / output_filename

    try:

        # =============================================
        # 5. LEER EXCEL
        # =============================================

        dataframe = pd.read_excel(
            input_path
        )

        rows = dataframe.to_dict(
            orient="records"
        )

        # =============================================
        # 6. OBTENER MAPPING
        # =============================================

        mapping = conversion.get(
            "mapping",
            {},
        )

        # =============================================
        # 7. OBTENER COLUMNAS SELECCIONADAS
        # =============================================

        configured_columns = conversion.get(
            "selected_columns"
        )

        selected_columns_list = None

        # ---------------------------------------------
        # Selección manual desde la interfaz
        # ---------------------------------------------

        if selected_columns is not None:

            try:

                selected_columns_list = json.loads(
                    selected_columns
                )

            except json.JSONDecodeError:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "La selección de columnas "
                        "no tiene un formato válido."
                    ),
                )

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

        # ---------------------------------------------
        # Configuración guardada
        # ---------------------------------------------

        else:

            selected_columns_list = (
                configured_columns
            )

        # =============================================
        # 8. VALIDAR COLUMNAS
        # =============================================

        if selected_columns_list is not None:

            missing_columns = [
                column
                for column
                in selected_columns_list
                if column not in dataframe.columns
            ]

            if missing_columns:

                raise HTTPException(
                    status_code=400,
                    detail={
                        "message": (
                            "Algunas columnas "
                            "seleccionadas no existen "
                            "en el Excel."
                        ),
                        "missing_columns": (
                            missing_columns
                        ),
                    },
                )

        # =============================================
        # 9. CONFIGURACIÓN DE VALIDACIÓN
        # =============================================

        validation_config = conversion.get(
            "validation",
            {},
        )

        required_fields = (
            validation_config.get(
                "required_fields",
                [],
            )
        )

        # =============================================
        # 10. MAPEAR
        # =============================================

        mapper = ExcelMapper(
            mapping=mapping,
            selected_columns=selected_columns_list,
        )

        mapped_rows = mapper.map_rows(
            rows
        )

        # =============================================
        # 11. OBTENER TRANSFORMACIONES
        # =============================================

        configured_transformations = (
            conversion.get(
                "transformations",
                {}
            )
        )

        # ---------------------------------------------
        # Copiamos la configuración para no modificar
        # directamente la configuración del cliente.
        # ---------------------------------------------

        if isinstance(
            configured_transformations,
            dict,
        ):

            transformation_config = (
                configured_transformations.copy()
            )

        else:

            transformation_config = {}

        # =============================================
        # 12. TRANSFORMACIONES DESDE LA INTERFAZ
        # =============================================

        if transformations is not None:

            try:

                manual_transformations = json.loads(
                    transformations
                )

            except json.JSONDecodeError:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Las transformaciones "
                        "no tienen un formato válido."
                    ),
                )

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

            # -----------------------------------------
            # Las operaciones creadas desde la interfaz
            # sustituyen las operaciones guardadas.
            #
            # Las demás reglas del cliente, como:
            #
            # "Y (m)": {
            #     "round": 2
            # }
            #
            # se mantienen.
            # -----------------------------------------

            transformation_config[
                "_operations"
            ] = manual_transformations

        # =============================================
        # 13. TRANSFORMAR
        # =============================================

        transformer = DataTransformer(
            transformations=transformation_config
        )

        transformed_rows = (
            transformer.transform_rows(
                mapped_rows
            )
        )

        # =============================================
        # 14. VALIDAR
        # =============================================

        validator = DataValidator(
            required_fields=required_fields
        )

        validation_result = (
            validator.validate_rows(
                transformed_rows
            )
        )

        if not validation_result["valid"]:

            raise HTTPException(
                status_code=400,
                detail={
                    "message": (
                        "El Excel contiene errores "
                        "de validación."
                    ),
                    "validation": (
                        validation_result
                    ),
                },
            )

        # =============================================
        # 15. GENERAR EXCEL
        # =============================================

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
                f"Error durante la conversión: "
                f"{error}"
            ),
        )

    # =================================================
    # 16. DESCARGAR RESULTADO
    # =================================================

    return FileResponse(
        path=output_path,
        filename=output_filename,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )