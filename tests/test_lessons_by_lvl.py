from datetime import datetime
from app.services.lesson import get_lessons_by_level
from app.database.models import UserExamResult, UserProgress


def test_get_lessons_basic_level(db_session, sample_user, course_and_lessons, active_exam):
    exam_result = UserExamResult(
        user_id=sample_user.id,
        exam_id=active_exam.id,
        total_score=30,
        level_assigned="basic",
        taken_at=datetime.now()
    )
    db_session.add(exam_result)
    db_session.commit()

    result = get_lessons_by_level(db_session, sample_user)
    assert result["level"] == "basic"
    assert len(result["lessons"]) == 5
    assert result["lessons"][0]["title"].startswith("Basic")
    assert result["next_lesson_id"] == result["lessons"][0]["id"]


def test_get_lessons_intermediate_level(db_session, sample_user, course_and_lessons, active_exam):
    exam_result = UserExamResult(
        user_id=sample_user.id,
        exam_id=active_exam.id,
        total_score=75,
        level_assigned="intermediate",
        taken_at=datetime.now()
    )
    db_session.add(exam_result)
    db_session.commit()

    result = get_lessons_by_level(db_session, sample_user)
    print(result)

    assert result["level"] == "intermediate"
    assert len(result["lessons"]) == 5
    assert result["lessons"][0]["order_in_course"] == 6


def test_next_lesson_respects_progress(db_session, sample_user, course_and_lessons, active_exam):
    exam_result = UserExamResult(
        user_id=sample_user.id,
        exam_id=active_exam.id,
        total_score=20,
        level_assigned="basic",
        taken_at=datetime.now()
    )
    db_session.add(exam_result)
    db_session.commit()

    _, lessons = course_and_lessons
    first = lessons[0]
    db_session.add(UserProgress(user_id=sample_user.id, lesson_id=first.id))
    db_session.commit()

    result = get_lessons_by_level(db_session, sample_user)

    assert result["next_lesson_id"] == result["lessons"][1]["id"]


def test_all_lessons_completed(db_session, sample_user, course_and_lessons, active_exam):
    exam_result = UserExamResult(
        user_id=sample_user.id,
        exam_id=active_exam.id,
        total_score=20,
        level_assigned="basic",
        taken_at=datetime.now()
    )
    db_session.add(exam_result)
    db_session.commit()

    _, lessons = course_and_lessons
    for lesson in lessons[:5]:
        db_session.add(UserProgress(user_id=sample_user.id, lesson_id=lesson.id))

    db_session.commit()

    result = get_lessons_by_level(db_session, sample_user)

    assert result["next_lesson_id"] is None
    assert len(result["lessons"]) == 5