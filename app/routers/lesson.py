from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database.connection import get_db
from app.database.models import User
from app.schemas.lesson import LessonOut, UserLessonsOut
from app.services.lesson import get_lesson_service, get_lessons_by_level, get_next_lesson_navigation

router = APIRouter(prefix="/module", tags=["Modules"])

@router.get("/lessons", response_model=UserLessonsOut)
def get_user_lessons(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_lessons_by_level(db, current_user)

@router.get("/{lesson_id}", response_model=LessonOut)
def get_lesson(lesson_id: str, db: Session = Depends(get_db)):
    return get_lesson_service(lesson_id, db)

@router.get("/{lesson_id}/navigation")
def get_lesson_navigation(lesson_id: str, db: Session = Depends(get_db)):
    return get_next_lesson_navigation(lesson_id, db)
