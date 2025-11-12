from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, progress, quiz, lesson

app = FastAPI(title="CyberSec Platform")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Servidor FastAPI funcionando correctamente 🚀"}


# Routers
app.include_router(auth.router)
app.include_router(lesson.router)
app.include_router(progress.router)
app.include_router(quiz.router)