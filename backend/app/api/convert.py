from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from backend.app.converter.excel_writer import ExcelWriter


router = APIRouter(prefix="/api", tags=["Conversion"])


BASE_DIR = Path(__file__).resolve().parents[3]
INPUT_DIR = BASE_DIR / "data" / "input"
OUTPUT_DIR = BASE_DIR / "data" / "output"


@router.post("/convert")
def convert_excel(filename: str):
    """
    Convierte un Excel de entrada y genera
    un archivo Excel de salida.

    La transformación real se añadirá cuando
    tengamos el formato definitivo de CONTASOL.
    """

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

    output_filename = f"CONTASOL_{input_path.stem}.xlsx"
    output_path = OUTPUT_DIR / output_filename

    try:
        # De momento generamos una copia estructurada
        # para probar el flujo completo.
        import pandas as pd

        dataframe = pd.read_excel(input_path)

        rows = dataframe.to_dict(orient="records")

        writer = ExcelWriter()
        writer.write(rows, output_path)

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