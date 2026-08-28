from pathlib import Path
import shutil

from fastapi import APIRouter, File, HTTPException, UploadFile


router = APIRouter(
    prefix="/api",
    tags=["Excel"],
)


BASE_DIR = Path(__file__).resolve().parents[3]

INPUT_DIR = BASE_DIR / "data" / "input"


ALLOWED_EXTENSIONS = {
    ".xlsx",
    ".xls",
}


@router.post("/upload")
async def upload_excel(
    file: UploadFile = File(...)
):
    """Recibe un archivo Excel y lo guarda temporalmente."""

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail=(
                "No se ha seleccionado ningún archivo."
            ),
        )


    extension = Path(
        file.filename
    ).suffix.lower()


    if extension not in ALLOWED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail=(
                "Solo se admiten archivos Excel "
                ".xlsx o .xls."
            ),
        )


    INPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    destination = (
        INPUT_DIR /
        Path(file.filename).name
    )


    with destination.open("wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer,
        )


    return {
        "status": "ok",
        "filename": destination.name,
        "message": (
            "Archivo recibido correctamente."
        ),
    }