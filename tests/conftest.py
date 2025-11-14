import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer

from app.database.connection import Base, get_db
from fastapi.testclient import TestClient

from app.database.models import User, Exam, Question, Answer, Course, Lesson
from app.main import app
from app.services.lesson import LEVEL_RANGES


@pytest.fixture(scope="session")
def pg_container():
    with PostgresContainer("postgres:15") as postgres:
        yield postgres

@pytest.fixture(scope="session")
def test_engine(pg_container):
    engine = create_engine(pg_container.get_connection_url())
    Base.metadata.create_all(bind=engine)
    return engine

@pytest.fixture
def db_session(test_engine):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(test_engine):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture(autouse=True)
def clean_tables(db_session):
    db_session.execute(text("TRUNCATE lesson RESTART IDENTITY CASCADE;"))
    db_session.execute(text("TRUNCATE course RESTART IDENTITY CASCADE;"))
    db_session.execute(text("TRUNCATE user_exam_result RESTART IDENTITY CASCADE;"))
    db_session.execute(text("TRUNCATE user_progress RESTART IDENTITY CASCADE;"))
    db_session.commit()
@pytest.fixture
def register_user(client: TestClient):
    payload = {
        "first_name": "Juliana",
        "last_name": "Ramírez",
        "email": "juliana@example.com",
        "password": "supersegura123"
    }
    response = client.post("/auth/register", json=payload)
    return response


@pytest.fixture
def sample_user(db_session):
    uid = uuid.uuid4().hex[:6]
    user = User(
        first_name="Test",
        last_name="User",
        email=f"test_{uid}@example.com",
        password_hash="hashed123*",
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def auth_user(client, db_session):
    email = f"user_{uuid.uuid4().hex[:6]}@example.com"
    password = "supersegura123"
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
    assert login.status_code == 200
    token = login.json()["access_token"]

    user = db_session.query(User).filter_by(email=email).first()
    return {
        "user": user,
        "token": token,
        "email": email,
        "password": password
    }

@pytest.fixture
def active_exam(db_session):
    exam = Exam(
        title="Examen de prueba",
        description="Prueba activa",
        is_active=True
    )
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

@pytest.fixture
def course_and_lessons(db_session):
    course = Course(
        title="Curso Cyber",
        description="Intro",
        level="basic"
    )
    db_session.add(course)
    db_session.commit()

    lessons = []

    for level_name, (start, end) in LEVEL_RANGES.items():
        for order in range(start, end + 1):
            prefix = level_name.capitalize()
            title = f"{prefix} {order}"

            l = Lesson(
                id=uuid.uuid4(),
                course_id=course.id,
                title=title,
                content_type="texto",
                text_content=f"Contenido {level_name}",
                order_in_course=order,
            )
            lessons.append(l)

    db_session.add_all(lessons)
    db_session.commit()

    return course, lessons

@pytest.fixture
def inactive_exam(db_session):
    exam = Exam(title="Inactivo", description="No disponible", is_active=False)
    db_session.add(exam)
    db_session.commit()
    return exam
