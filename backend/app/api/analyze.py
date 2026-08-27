from pathlib import Path

from fastapi import APIRouter, HTTPException

from backend.app.converter.excel_reader import ExcelReader


router = APIRouter(prefix="/api", tags=["Excel"])


BASE_DIR = Path(__file__).resolve().parents[3]
INPUT_DIR = BASE_DIR / "data" / "input"


@router.get("/analyze/{filename}")
def analyze_excel(filename: str):
    """Analiza un Excel almacenado en data/input."""

    file_path = INPUT_DIR / Path(filename).name

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="El archivo no existe.",
        )

    if file_path.suffix.lower() != ".xlsx":
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser un Excel .xlsx.",
        )

    try:
        reader = ExcelReader(file_path)

        return reader.analyze()

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"No se pudo analizar el Excel: {error}",
        ) from error