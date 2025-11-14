from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from app.database.models.user_exam_result import UserExamResult
from app.database.models.exam import Exam
from app.database.models.user import User


def create_and_login(client, email="test@example.com", password="testpassword"):
    client.post("/auth/register", json={
        "first_name": "Test",
        "last_name": "User",
        "email": email,
        "password": password
    })

    login = client.post("/auth/login", json={
        "email": email,
        "password": password
    })

    assert login.status_code == 200, login.json()
    return login.json()["access_token"]


def get_user_from_db(db_session, email):
    return db_session.query(User).filter(User.email == email).first()


def test_quiz_level_initial(client: TestClient):
    token = create_and_login(client, "initial@example.com")

    response = client.get(
        "/quiz/level",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["level"] in ["basic"]

def test_quiz_level_single_result(client: TestClient, db_session):
    email = "single@example.com"
    token = create_and_login(client, email)

    user = get_user_from_db(db_session, email)

    exam = Exam(title="Exam1", is_active=True)
    db_session.add(exam)
    db_session.commit()

    result = UserExamResult(
        user_id=user.id,
        exam_id=exam.id,
        total_score=80,
        level_assigned="intermediate",
        taken_at=datetime.now()
    )
    db_session.add(result)
    db_session.commit()

    response = client.get(
        "/quiz/level",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["level"] == "intermediate"

def test_quiz_level_multiple_results(client: TestClient, db_session):
    email = "multi@example.com"
    token = create_and_login(client, email)

    user = get_user_from_db(db_session, email)

    exam = Exam(title="Exam2", is_active=True)
    db_session.add(exam)
    db_session.commit()

    older = UserExamResult(
        user_id=user.id,
        exam_id=exam.id,
        total_score=20,
        level_assigned="basic",
        taken_at=datetime.now() - timedelta(days=1)
    )
    newer = UserExamResult(
        user_id=user.id,
        exam_id=exam.id,
        total_score=95,
        level_assigned="advanced",
        taken_at=datetime.now()
    )

    db_session.add(older)
    db_session.add(newer)
    db_session.commit()

    response = client.get(
        "/quiz/level",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["level"] == "advanced"

def test_quiz_level_without_token(client: TestClient):
    response = client.get("/quiz/level")
    assert response.status_code == 401

def test_quiz_level_invalid_token(client: TestClient):
    response = client.get(
        "/quiz/level",
        headers={"Authorization": "Bearer invalid123"}
    )
    assert response.status_code == 401

def test_quiz_level_zero_score(client: TestClient, db_session):
    email = "zeroscore@example.com"
    token = create_and_login(client, email)

    user = get_user_from_db(db_session, email)

    exam = Exam(title="ExamZero", is_active=True)
    db_session.add(exam)
    db_session.commit()

    result = UserExamResult(
        user_id=user.id,
        exam_id=exam.id,
        total_score=0,
        level_assigned="basic",
        taken_at=datetime.now()
    )
    db_session.add(result)
    db_session.commit()

    response = client.get(
        "/quiz/level",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["level"] == "basic"

def test_quiz_level_max_score(client: TestClient, db_session):
    email = "perfect@example.com"
    token = create_and_login(client, email)

    user = get_user_from_db(db_session, email)

    exam = Exam(title="ExamMax", is_active=True)
    db_session.add(exam)
    db_session.commit()

    result = UserExamResult(
        user_id=user.id,
        exam_id=exam.id,
        total_score=100,
        level_assigned="advanced",
        taken_at=datetime.now()
    )
    db_session.add(result)
    db_session.commit()

    response = client.get(
        "/quiz/level",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["level"] == "advanced"
