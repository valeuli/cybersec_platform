from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.database.connection import get_db
from app.database.models.user import User
from app.schemas.progress import ProgressOut
from app.services.progress import track_progress_service

router = APIRouter(prefix="/progress/module", tags=["Progress"])

@router.post("/{module_id}/track")
def track_progress(
    module_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = track_progress_service(module_id, db, current_user)
    return ProgressOut(
        user_id=record.user_id,
        lesson_id=record.lesson_id,
        last_accessed_at=record.last_accessed_at,
        message="Progreso registrado correctamente",
    )
