from fastapi import FastAPI
from app.routers import auth, progress, quiz, lesson

app = FastAPI(title="CyberSec Platform")

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Servidor FastAPI funcionando correctamente 🚀"}


# Routers
app.include_router(auth.router)
app.include_router(lesson.router)
app.include_router(progress.router)
app.include_router(quiz.router)