from pydantic import BaseModel, UUID4
from typing import List


class AnswerSubmit(BaseModel):
    answer_id: UUID4


class AnswerOut(BaseModel):
    id: UUID4
    answer_text: str

class QuestionOut(BaseModel):
    index: int
    question: str
    answers: List[AnswerOut]

class AttemptCreated(BaseModel):
    attempt_id: UUID4
    total_questions: int
    message: str

class QuizResultOut(BaseModel):
    message: str
    total_correct: int
    score: float
    level_assigned: str