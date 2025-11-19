import uuid
import pytest
from datetime import datetime, timedelta, timezone
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


def test_start_quiz_attempt_success(db_session, sample_user, active_exam):
    result = start_quiz_attempt(db_session, sample_user)
    assert "attempt_id" in result
    assert result["message"] == "Intento de examen creado."


def test_get_question_success(db_session, sample_user, active_exam, basic_question_set):
    attempt = UserExamResult(user_id=sample_user.id, exam_id=active_exam.id, taken_at=datetime.now(timezone.utc))
    db_session.add(attempt)
    db_session.commit()

    res = get_question(db_session, attempt.id, 1, sample_user)
    assert "question" in res
    assert "answers" in res
    assert res["index"] == 1


def test_get_question_index_out_of_range(db_session, sample_user, active_exam, basic_question_set):
    attempt = UserExamResult(user_id=sample_user.id, exam_id=active_exam.id, taken_at=datetime.now(timezone.utc))
    db_session.add(attempt)
    db_session.commit()
    with pytest.raises(HTTPException):
        get_question(db_session, attempt.id, 10, sample_user)


def test_submit_answer_success(db_session, sample_user, active_exam, basic_question_set):
    attempt = UserExamResult(user_id=sample_user.id, exam_id=active_exam.id, taken_at=datetime.now(timezone.utc))
    db_session.add(attempt)
    db_session.commit()
    answer = db_session.query(Answer).first()

    res = submit_answer(db_session, attempt.id, answer.id, 1, sample_user)
    assert res["message"] == "Respuesta registrada."


def test_submit_answer_invalid_id(db_session, sample_user, active_exam):
    attempt = UserExamResult(user_id=sample_user.id, exam_id=active_exam.id, taken_at=datetime.now(timezone.utc))
    db_session.add(attempt)
    db_session.commit()
    with pytest.raises(HTTPException):
        submit_answer(db_session, attempt.id, "nonexistent-id", 1, sample_user)


def test_submit_answer_not_found(db_session, sample_user, active_exam):
    attempt = UserExamResult(user_id=sample_user.id, exam_id=active_exam.id, taken_at=datetime.now(timezone.utc))
    db_session.add(attempt)
    db_session.commit()
    random_uuid = "e4bc07dd-43c7-478c-ad41-54ccc17cdf24"
    with pytest.raises(HTTPException):
        submit_answer(db_session, attempt.id, random_uuid, 1, sample_user)


def test_calculate_level_progression_correct_scores(db_session, sample_user, active_exam, basic_question_set):
    attempt = UserExamResult(user_id=sample_user.id, exam_id=active_exam.id, taken_at=datetime.now(timezone.utc))
    db_session.add(attempt)
    db_session.commit()
    answers = [
        UserExamAnswer(result_id=attempt.id, question_id=q.id, answer_id=None, is_correct=True)
        for q in basic_question_set
    ]
    db_session.add_all(answers)
    db_session.commit()

    res = calculate_level_progression(db_session, attempt.id)
    assert res["total_score"] >= 0
    assert res["level_assigned"] in ["initial", "basic", "intermediate", "advanced"]


def test_finish_quiz_success(db_session, sample_user, active_exam, basic_question_set):
    attempt = UserExamResult(user_id=sample_user.id, exam_id=active_exam.id, taken_at=datetime.now(timezone.utc))
    db_session.add(attempt)
    db_session.commit()

    all_questions = db_session.query(Question).filter(Question.is_active == True).all()
    for q in all_questions:
        db_session.add(
            UserExamAnswer(
                result_id=attempt.id,
                question_id=q.id,
                answer_id=None,
                is_correct=True
            )
        )
    db_session.commit()

    res = finish_quiz(db_session, attempt.id, sample_user)
    assert "message" in res
    assert "total_score" in res
    assert "level_assigned" in res


def test_validate_attempt_time_expired():
    start = datetime.now() - timedelta(minutes=40)
    with pytest.raises(HTTPException):
        validate_attempt_time(start, 30)
