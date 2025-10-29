from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models.lesson import Lesson
from app.database.models.user_progress import UserProgress
from app.database.models.user import User
from app.core.security import get_current_user

router = APIRouter(prefix="/progress/module", tags=["Progress"])

@router.post("/{module_id}/track")
def track_progress(
    module_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lesson = db.query(Lesson).filter(Lesson.id == module_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Módulo no encontrado")

    record = (
        db.query(UserProgress)
        .filter(
            UserProgress.user_id == current_user.id,
            UserProgress.lesson_id == module_id
        )
        .first()
    )

    if record:
        record.last_accessed_at = datetime.utcnow()
    else:
        record = UserProgress(
            user_id=current_user.id,
            lesson_id=module_id,
            last_accessed_at=datetime.utcnow(),
        )
        db.add(record)

    db.commit()
    return {"message": "Progreso registrado correctamente"}
