from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database.connection import test_connection
from app.routers import auth
app = FastAPI(title="CyberSec Platform")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Evento de inicio
    try:
        test_connection()
        print("✅ Conexión a la base de datos exitosa")
    except Exception as e:
        print("⚠️ Error al conectar con la base de datos:", e)
    yield
    # Evento de cierre (si luego querés agregar algo, como cerrar sesiones)
    print("👋 Cerrando aplicación...")

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Servidor FastAPI funcionando correctamente 🚀"}


# Routers
app.include_router(auth.router)