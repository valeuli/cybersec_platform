from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.core.security import get_current_user
from app.database.models.user import User
from app.schemas.quiz import AttemptCreated, QuestionOut, QuizResultOut
from app.services.quiz import (
    start_quiz_attempt,
    get_question,
    submit_answer,
    finish_quiz,
    get_user_level,
)

router = APIRouter(prefix="/quiz", tags=["Quiz"])

@router.post("/attempts", response_model=AttemptCreated, status_code=201)
def start_attempt(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return start_quiz_attempt(db, current_user)

@router.get("/attempts/{attempt_id}/questions", response_model=QuestionOut)
def get_quiz_question(attempt_id: str, index: int = 1, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_question(db, attempt_id, index, current_user)

@router.post("/attempts/{attempt_id}/answers")
def submit_quiz_answer(attempt_id: str, data: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return submit_answer(db, attempt_id, data.get("answer_id"), current_user)

@router.post("/attempts/{attempt_id}/finish", response_model=QuizResultOut)
def finish_quiz_attempt(attempt_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return finish_quiz(db, attempt_id, current_user)

@router.get("/level")
def get_user_level_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_level(db, current_user)
