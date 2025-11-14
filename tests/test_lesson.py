import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database.models import Course
from app.database.models.lesson import Lesson
from app.main import app

client = TestClient(app)

def create_lesson(db: Session):
    course = Course(
        id=uuid.uuid4(),
        title="Curso Test",
        description="Desc",
        level="basic"
    )
    db.add(course)
    db.commit()

    lesson = Lesson(
        id=str(uuid.uuid4()),
        course_id=course.id,
        content_type="texto",
        title="Introducción a la ciberseguridad",
        content_url="www.testing.com",
        text_content="Contenido de prueba sobre ciberseguridad.",
        order_in_course=1,
    )
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    print("LESSON COURSE_ID:", lesson.course_id, type(lesson.course_id))
    return lesson


def test_get_lesson_success(client, db_session):
    lesson = create_lesson(db_session)
    response = client.get(f"/module/{lesson.id}")
    data = response.json()


    assert response.status_code == 200
    assert data["id"] == str(lesson.id)
    assert data["title"] == "Introducción a la ciberseguridad"
    assert data["content_type"] == "texto"


def test_get_lesson_not_found(client):
    non_existent_id = str(uuid.uuid4())
    response = client.get(f"/module/{non_existent_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Módulo no encontrado"


def test_get_lesson_invalid_id(client):
    invalid_id = "not-a-uuid"
    response = client.get(f"/module/{invalid_id}")
    assert response.status_code == 400
    assert response.json()["detail"] == "ID inválido"
