from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database.models import Question, Answer, Exam, UserExamAnswer
from app.database.models.user_exam_result import UserExamResult
from app.database.models.user import User


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

    answers = db.query(UserExamAnswer).filter(UserExamAnswer.result_id == attempt_id).all()
    total_correct = sum(1 for a in answers if a.is_correct)
    total_questions = db.query(Question).count()

    if total_questions == 0:
        raise HTTPException(status_code=400, detail="No hay preguntas en el examen.")

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