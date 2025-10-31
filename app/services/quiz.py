from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database.models import Question, Answer, Exam, UserExamAnswer
from app.database.models.user_exam_result import UserExamResult
from app.database.models.user import User
from app.utils.time_validator import validate_attempt_time


def start_quiz_attempt(db: Session, current_user: User):
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


def get_question(db: Session, attempt_id: str, index: int, current_user: User):
    attempt = db.query(UserExamResult).filter(
        UserExamResult.id == attempt_id,
        UserExamResult.user_id == current_user.id
    ).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Intento no encontrado.")

    questions = db.query(Question).filter(Question.is_active == True).order_by(Question.created_at).all()
    if index < 1 or index > len(questions):
        raise HTTPException(status_code=400, detail="Índice fuera de rango.")

    question = questions[index - 1]
    answers = db.query(Answer).filter(Answer.question_id == question.id).all()

    return {
        "index": index,
        "question": question.question_text,
        "answers": [{"id": a.id, "answer_text": a.answer_text} for a in answers],
    }


def submit_answer(db: Session, attempt_id: str, answer_id: str, current_user: User):
    answer = db.query(Answer).filter(Answer.id == answer_id).first()
    if not answer:
        raise HTTPException(status_code=404, detail="Respuesta no encontrada.")

    record = UserExamAnswer(
        result_id=attempt_id,
        question_id=answer.question_id,
        answer_id=answer.id,
        is_correct=answer.is_correct,
        created_at=datetime.utcnow(),
    )
    db.add(record)
    db.commit()
    return {"message": "Respuesta guardada exitosamente."}


def finish_quiz(db: Session, attempt_id: str, current_user: User):
    attempt = db.query(UserExamResult).filter(
        UserExamResult.id == attempt_id,
        UserExamResult.user_id == current_user.id
    ).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Intento no encontrado.")

    validate_attempt_time(attempt.taken_at)

    result_data = calculate_level_progression(db, attempt_id)
    attempt.total_score = result_data["total_score"]
    attempt.level_assigned = result_data["level_assigned"]
    db.commit()

    return {"message": "Examen finalizado.", **result_data}

def calculate_level_progression(db: Session, attempt_id: str):
    answers = db.query(UserExamAnswer).filter(UserExamAnswer.result_id == attempt_id).all()
    if not answers:
        raise HTTPException(status_code=400, detail="No hay respuestas registradas para este intento.")

    question_ids = [a.question_id for a in answers]
    questions = db.query(Question).filter(Question.id.in_(question_ids)).all()

    correct_by_level = {"basic": 0, "intermediate": 0, "advanced": 0}
    total_by_level = {"basic": 0, "intermediate": 0, "advanced": 0}

    for q in questions:
        level = q.level
        total_by_level[level] += 1
        related_answer = next((a for a in answers if a.question_id == q.id), None)
        if related_answer and related_answer.is_correct:
            correct_by_level[level] += 1

    score_basic = round((correct_by_level["basic"] / total_by_level["basic"]) * 20, 2) if total_by_level["basic"] else 0
    score_intermediate = round((correct_by_level["intermediate"] / total_by_level["intermediate"]) * 50, 2) if total_by_level["intermediate"] else 0
    score_advanced = round((correct_by_level["advanced"] / total_by_level["advanced"]) * 30, 2) if total_by_level["advanced"] else 0

    total_score = score_basic + score_intermediate + score_advanced

    if total_score >= 95:
        level = "avanzado"
    elif total_score >= 70:
        level = "intermedio"
    elif total_score >= 20:
        level = "básico"
    else:
        level = "inicial"

    return {
        "score_basic": score_basic,
        "score_intermediate": score_intermediate,
        "score_advanced": score_advanced,
        "total_score": total_score,
        "level_assigned": level,
    }