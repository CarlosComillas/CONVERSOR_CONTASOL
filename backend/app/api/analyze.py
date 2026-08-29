from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

from backend.app.converter.excel_reader import ExcelReader


router = APIRouter(
    prefix="/api",
    tags=["Excel"],
)


BASE_DIR = Path(__file__).resolve().parents[3]

INPUT_DIR = BASE_DIR / "data" / "input"


# =====================================================
# ANALIZAR EXCEL
# =====================================================

@router.get("/analyze/{filename}")
def analyze_excel(
    filename: str,
):
    """
    Analiza un Excel almacenado en data/input.

    Se admiten archivos .xlsx y .xls.
    """

    file_path = (
        INPUT_DIR /
        Path(filename).name
    )

    # =================================================
    # COMPROBAR QUE EXISTE
    # =================================================

    if not file_path.exists():

        raise HTTPException(
            status_code=404,
            detail="El archivo no existe.",
        )

    # =================================================
    # COMPROBAR EXTENSIÓN
    # =================================================

    if file_path.suffix.lower() not in {
        ".xlsx",
        ".xls",
    }:

        raise HTTPException(
            status_code=400,
            detail=(
                "El archivo debe ser un Excel "
                ".xlsx o .xls."
            ),
        )

    # =================================================
    # ANALIZAR
    # =================================================

    try:

        reader = ExcelReader(
            file_path
        )

        return reader.analyze()

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"No se pudo analizar el Excel: "
                f"{error}"
            ),
        ) from error


# =====================================================
# PREVIEW PAGINADO
# =====================================================

@router.get("/preview/{filename}")
def preview_excel(
    filename: str,
    sheet: str = Query(...),
    page: int = Query(
        1,
        ge=1,
    ),
    page_size: int = Query(
        25,
        ge=1,
        le=100,
    ),
):
    """
    Devuelve una página concreta de una hoja
    del Excel.

    Ejemplo:

    /api/preview/archivo.xlsx
        ?sheet=IMAT-3-A
        &page=2
        &page_size=25
    """

    file_path = (
        INPUT_DIR /
        Path(filename).name
    )

    # =================================================
    # COMPROBAR QUE EXISTE
    # =================================================

    if not file_path.exists():

        raise HTTPException(
            status_code=404,
            detail="El archivo no existe.",
        )

    # =================================================
    # COMPROBAR EXTENSIÓN
    # =================================================

    if file_path.suffix.lower() not in {
        ".xlsx",
        ".xls",
    }:

        raise HTTPException(
            status_code=400,
            detail=(
                "El archivo debe ser un Excel "
                ".xlsx o .xls."
            ),
        )

    # =================================================
    # OBTENER PREVIEW
    # =================================================

    try:

        reader = ExcelReader(
            file_path
        )

        sheet_names = (
            reader.get_sheet_names()
        )

        if sheet not in sheet_names:

            raise HTTPException(
                status_code=404,
                detail=(
                    f"No existe la hoja "
                    f"'{sheet}'."
                ),
            )

        return reader.get_preview(
            sheet_name=sheet,
            page=page,
            page_size=page_size,
        )

    except HTTPException:

        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"No se pudo obtener la "
                f"vista previa: {error}"
            ),
        ) from error