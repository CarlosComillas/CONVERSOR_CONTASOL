from fastapi import FastAPI

app = FastAPI(
    title="TÍO PABLO",
    description="Conversor de archivos Excel para CONTASOL",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "TÍO PABLO funcionando correctamente",
        "version": "0.1.0",
    }