from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from backend.app.converter.excel_writer import ExcelWriter
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
        client = config_manager.load_client(client_id)

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"No existe el cliente: {client_id}",
        )

    # -------------------------------------------------
    # 2. Comprobar que existe la conversión
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

    # -------------------------------------------------
    # 5. Leer Excel
    # -------------------------------------------------

    try:
        dataframe = pd.read_excel(input_path)

        rows = dataframe.to_dict(
            orient="records"
        )

        # -------------------------------------------------
        # 6. Obtener mapping de la configuración
        # -------------------------------------------------

        mapping = conversion.get(
            "mapping",
            {},
        )

        # -------------------------------------------------
        # 7. Aplicar el mapping
        # -------------------------------------------------

        from backend.app.converter.mapper import ExcelMapper

        mapper = ExcelMapper(mapping)

        mapped_rows = mapper.map_rows(rows)

        # -------------------------------------------------
        # 8. Generar archivo
        # -------------------------------------------------

        writer = ExcelWriter()

        writer.write(
            mapped_rows,
            output_path,
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Error durante la conversión: {error}",
        )

    return FileResponse(
        path=output_path,
        filename=output_filename,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )