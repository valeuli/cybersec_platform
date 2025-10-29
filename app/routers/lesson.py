from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.lesson import LessonOut
from app.services.lesson import get_lesson_service

router = APIRouter(prefix="/module", tags=["Modules"])

@router.get("/{lesson_id}", response_model=LessonOut)
def get_lesson(lesson_id: str, db: Session = Depends(get_db)):
    return get_lesson_service(lesson_id, db)
