from fastapi import FastAPI
from app.database.connection import test_connection
app = FastAPI(title="CyberSec Platform")

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Servidor FastAPI funcionando correctamente 🚀"}


test_connection()