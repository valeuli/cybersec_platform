from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import Question, Answer, Exam, UserExamAnswer
from app.database.models.user_exam_result import UserExamResult
from app.core.security import get_current_user
from app.database.models.user import User
from datetime import datetime
from sqlalchemy.sql import func

router = APIRouter(prefix="/quiz", tags=["Quiz"])

@router.post("/attempts", status_code=201)
def start_quiz_attempt(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    exam = db.query(Exam).filter(Exam.is_active == True).first()
    if not exam:
        raise HTTPException(status_code=404, detail="No hay exámenes activos.")

    attempt = UserExamResult(
        user_id=current_user.id,
        exam_id=exam.id,
        total_score=None,
        level_assigned=None,
        taken_at=datetime.utcnow(),
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return {"attempt_id": attempt.id, "message": "Intento de examen creado."}

@router.get("/attempts/{attempt_id}/questions")
def get_question(
    attempt_id: str,
    index: int = 1,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attempt = db.query(UserExamResult).filter(UserExamResult.id == attempt_id, UserExamResult.user_id == current_user.id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Intento no encontrado.")

    questions = db.query(Question).filter(Question.is_active == True).order_by(Question.created_at).all()
    if index < 1 or index > len(questions):
        raise HTTPException(status_code=400, detail="Índice de pregunta fuera de rango.")

    question = questions[index - 1]
    answers = db.query(Answer).filter(Answer.question_id == question.id).all()

    return {
        "index": index,
        "question": question.question_text,
        "answers": [{"id": a.id, "answer_text": a.answer_text} for a in answers],
    }

@router.post("/attempts/{attempt_id}/answers")
def submit_answer(
    attempt_id: str,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    answer_id = data.get("answer_id")
    answer = db.query(Answer).filter(Answer.id == answer_id).first()
    if not answer:
        raise HTTPException(status_code=404, detail="Respuesta no encontrada.")

    record = UserExamAnswer(
        question_id=answer.question_id,
        answer_id=answer.id,
        is_correct=answer.is_correct,
        created_at=datetime.utcnow(),
    )
    db.add(record)
    db.commit()

    return {"message": "Respuesta guardada exitosamente."}

# 10. Finalizar examen
@router.post("/attempts/{attempt_id}/finish")
def finish_attempt(
    attempt_id: str,
    score: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    level = "basic"
    if score >= 80:
        level = "advanced"
    elif score >= 50:
        level = "intermediate"

    result = UserExamResult(
        user_id=current_user.id,
        exam_id=None,
        total_score=score,
        level_assigned=level,
        taken_at=datetime.utcnow(),
    )
    db.add(result)
    db.commit()
    return {"message": "Examen finalizado", "level_assigned": level}


@router.post("/attempts/{attempt_id}/finish")
def finish_quiz(
    attempt_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attempt = db.query(UserExamResult).filter(UserExamResult.id == attempt_id, UserExamResult.user_id == current_user.id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Intento no encontrado.")

    answers = db.query(UserExamAnswer).filter(UserExamAnswer.result_id == attempt_id).all()
    total_correct = sum(1 for a in answers if a.is_correct)
    total_questions = db.query(Question).count()

    score = round((total_correct / total_questions) * 100, 2)
    if score < 50:
        level = "básico"
    elif score < 80:
        level = "intermedio"
    else:
        level = "avanzado"

    attempt.total_score = score
    attempt.level_assigned = level
    db.commit()

    return {
        "message": "Examen finalizado.",
        "total_correct": total_correct,
        "score": score,
        "level_assigned": level,
    }
