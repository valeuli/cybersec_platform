from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.database.models.lesson import Lesson
from app.database.models.user_progress import UserProgress
from app.database.models.user import User

def track_progress_service(module_id: str, db: Session, current_user: User) -> UserProgress:
    lesson = db.query(Lesson).filter(Lesson.id == module_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Módulo no encontrado")

    record = (
        db.query(UserProgress)
        .filter(UserProgress.user_id == current_user.id, UserProgress.lesson_id == module_id)
        .first()
    )

    if record:
        record.last_accessed_at = datetime.utcnow()
    else:
        record = UserProgress(
            user_id=current_user.id,
            lesson_id=lesson.id,  # usa el UUID real de la lección
            last_accessed_at=datetime.utcnow(),
        )
        db.add(record)

    db.commit()
    db.refresh(record)
    return record