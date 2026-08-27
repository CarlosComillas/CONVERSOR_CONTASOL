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

config_manager = ConfigManager(CLIENTS_CONFIG_DIR)


@router.post("/convert")
def convert_excel(
    filename: str,
    client_id: str,
    conversion_id: str,
):
    """
    Convierte un Excel utilizando la configuración
    del cliente y de la conversión seleccionada.
    """

    # -------------------------------------------------
    # 1. Comprobar que existe el cliente
    # -------------------------------------------------

    try:
        config_manager.load_client(client_id)

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"No existe el cliente: {client_id}",
        )

    # -------------------------------------------------
    # 2. Cargar la conversión
    # -------------------------------------------------

    try:
        conversion = config_manager.load_conversion(
            client_id,
            conversion_id,
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No existe la conversión '{conversion_id}' "
                f"para el cliente '{client_id}'."
            ),
        )

    # -------------------------------------------------
    # 3. Comprobar que existe el Excel
    # -------------------------------------------------

    input_path = INPUT_DIR / filename

    if not input_path.exists():
        raise HTTPException(
            status_code=404,
            detail="No se encontró el archivo Excel.",
        )

    if input_path.suffix.lower() != ".xlsx":
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser un Excel .xlsx.",
        )

    # -------------------------------------------------
    # 4. Generar nombre del archivo de salida
    # -------------------------------------------------

    output_filename = (
        f"CONTASOL_{client_id}_{conversion_id}_"
        f"{input_path.stem}.xlsx"
    )

    output_path = OUTPUT_DIR / output_filename

    try:

        # -------------------------------------------------
        # 5. Leer Excel
        # -------------------------------------------------

        dataframe = pd.read_excel(input_path)

        rows = dataframe.to_dict(
            orient="records"
        )

        # -------------------------------------------------
        # 6. Obtener configuración
        # -------------------------------------------------

        mapping = conversion.get(
            "mapping",
            {},
        )

        validation_config = conversion.get(
            "validation",
            {},
        )

        required_fields = validation_config.get(
            "required_fields",
            [],
        )

        # -------------------------------------------------
        # 7. MAPEAR
        # -------------------------------------------------

        mapper = ExcelMapper(
            mapping=mapping
        )

        mapped_rows = mapper.map_rows(rows)

        # -------------------------------------------------
        # 8. TRANSFORMAR
        # -------------------------------------------------

        transformations = conversion.get(
            "transformations",
            {},
        )

        transformer = DataTransformer(transformations=transformations)

        transformed_rows = transformer.transform_rows(
            mapped_rows
        )

        # -------------------------------------------------
        # 9. VALIDAR
        # -------------------------------------------------

        validator = DataValidator(
            required_fields=required_fields
        )

        validation_result = validator.validate_rows(
            transformed_rows
        )

        if not validation_result["valid"]:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "El Excel contiene errores de validación.",
                    "validation": validation_result,
                },
            )

        # -------------------------------------------------
        # 10. GENERAR EXCEL
        # -------------------------------------------------

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
            detail=f"Error durante la conversión: {error}",
        )

    # -------------------------------------------------
    # 11. Descargar resultado
    # -------------------------------------------------

    return FileResponse(
        path=output_path,
        filename=output_filename,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )