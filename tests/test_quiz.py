import uuid
import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException
from app.services.quiz import (
    start_quiz_attempt,
    get_question,
    submit_answer,
    finish_quiz,
    calculate_level_progression
)
from app.utils.time_validator import validate_attempt_time
from app.database.models import Exam, Question, Answer, UserExamResult, UserExamAnswer
from app.database.models.user import User

@pytest.fixture
def sample_user(db_session):
    unique = uuid.uuid4().hex[:8]
    user = User(
        first_name="Test",
        last_name="User",
        email=f"test_{unique}@example.com",
        password_hash="hashed",
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def active_exam(db_session):
    exam = Exam(title="Examen general", description="Prueba activa", is_active=True)
    db_session.add(exam)
    db_session.commit()
    return exam

@pytest.fixture
def inactive_exam(db_session):
    exam = Exam(title="Inactivo", description="No disponible", is_active=False)
    db_session.add(exam)
    db_session.commit()
    return exam

@pytest.fixture
def basic_question_set(db_session):
    q1 = Question(question_text="¿Qué es ciberseguridad?", level="basic")
    q2 = Question(question_text="¿Qué es un malware?", level="basic")
    db_session.add_all([q1, q2])
    db_session.commit()

    a1 = Answer(question_id=q1.id, answer_text="Protección de sistemas", is_correct=True)
    a2 = Answer(question_id=q1.id, answer_text="Ataque informático", is_correct=False)
    a3 = Answer(question_id=q2.id, answer_text="Software malicioso", is_correct=True)
    a4 = Answer(question_id=q2.id, answer_text="Antivirus", is_correct=False)
    db_session.add_all([a1, a2, a3, a4])
    db_session.commit()

    return [q1, q2]


def test_start_quiz_attempt_success(db_session, sample_user, active_exam):
    result = start_quiz_attempt(db_session, sample_user)
    assert "attempt_id" in result
    assert result["message"] == "Intento de examen creado."

def test_start_quiz_attempt_no_active_exam(db_session, sample_user, inactive_exam):
    db_session.query(Exam).delete()
    db_session.commit()
    with pytest.raises(HTTPException) as exc:
        start_quiz_attempt(db_session, sample_user)
    assert exc.value.status_code == 404

def test_get_question_success(db_session, sample_user, active_exam, basic_question_set):
    attempt = UserExamResult(user_id=sample_user.id, exam_id=active_exam.id, taken_at=datetime.now())
    db_session.add(attempt)
    db_session.commit()

    res = get_question(db_session, attempt.id, 1, sample_user)
    assert "question" in res
    assert "answers" in res
    assert res["index"] == 1

def test_get_question_index_out_of_range(db_session, sample_user, active_exam, basic_question_set):
    attempt = UserExamResult(user_id=sample_user.id, exam_id=active_exam.id, taken_at=datetime.now())
    db_session.add(attempt)
    db_session.commit()
    with pytest.raises(HTTPException) as exc:
        get_question(db_session, attempt.id, 10, sample_user)
    assert exc.value.status_code == 400

def test_submit_answer_success(db_session, sample_user, active_exam, basic_question_set):
    attempt = UserExamResult(user_id=sample_user.id, exam_id=active_exam.id, taken_at=datetime.now())
    db_session.add(attempt)
    db_session.commit()
    answer = db_session.query(Answer).first()

    res = submit_answer(db_session, attempt.id, answer.id)
    assert res["message"] == "Respuesta guardada exitosamente."

def test_submit_answer_invalid_id(db_session, sample_user, active_exam):
    attempt = UserExamResult(user_id=sample_user.id, exam_id=active_exam.id, taken_at=datetime.now())
    db_session.add(attempt)
    db_session.commit()
    with pytest.raises(HTTPException) as exc:
        submit_answer(db_session, attempt.id, "nonexistent-id")
    assert exc.value.status_code == 400

def test_submit_answer_not_found(db_session, sample_user, active_exam):
    attempt = UserExamResult(user_id=sample_user.id, exam_id=active_exam.id, taken_at=datetime.now())
    db_session.add(attempt)
    db_session.commit()
    with pytest.raises(HTTPException) as exc:
        submit_answer(db_session, attempt.id, "e4bc07dd-43c7-478c-ad41-54ccc17cdf24")
    assert exc.value.status_code == 404

def test_calculate_level_progression_correct_scores(db_session, sample_user, active_exam, basic_question_set):
    attempt = UserExamResult(user_id=sample_user.id, exam_id=active_exam.id, taken_at=datetime.now())
    db_session.add(attempt)
    db_session.commit()
    answers = [
        UserExamAnswer(result_id=attempt.id, question_id=q.id, answer_id=None, is_correct=True)
        for q in basic_question_set
    ]
    db_session.add_all(answers)
    db_session.commit()

    res = calculate_level_progression(db_session, attempt.id)
    assert res["total_score"] > 0
    assert res["level_assigned"] in ["basic", "intermediate", "advanced"]

def test_finish_quiz_success(db_session, sample_user, active_exam, basic_question_set):
    attempt = UserExamResult(user_id=sample_user.id, exam_id=active_exam.id, taken_at=datetime.now())
    db_session.add(attempt)
    db_session.commit()

    for q in basic_question_set:
        db_session.add(UserExamAnswer(result_id=attempt.id, question_id=q.id, answer_id=None, is_correct=True))
    db_session.commit()

    res = finish_quiz(db_session, attempt.id, sample_user)
    assert "message" in res
    assert "total_score" in res
    assert "level_assigned" in res

def test_validate_attempt_time_expired():
    start = datetime.now() - timedelta(minutes=40)
    with pytest.raises(HTTPException) as exc:
        validate_attempt_time(start, 30)
    assert exc.value.status_code == 403
    assert "Tiempo de examen excedido" in exc.value.detail