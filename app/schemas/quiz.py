from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AnswerBase(BaseModel):
    text: str
    is_correct: bool


class AnswerCreate(AnswerBase):
    pass


class Answer(AnswerBase):
    id: int
    question_id: int

    model_config = ConfigDict(from_attributes=True)


class QuestionBase(BaseModel):
    text: str
    order: Optional[int] = None


class QuestionCreate(QuestionBase):
    answers: List[AnswerCreate]


class Question(QuestionBase):
    id: int
    quiz_id: int
    answers: List[Answer]

    model_config = ConfigDict(from_attributes=True)


class QuizBase(BaseModel):
    title: str
    description: Optional[str] = None


class QuizCreate(QuizBase):
    questions: List[QuestionCreate]


class Quiz(QuizBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool
    questions: List[Question]

    model_config = ConfigDict(from_attributes=True)


class AnswerSubmission(BaseModel):
    question_id: int
    answer_id: int


class QuizSubmission(BaseModel):
    quiz_id: int
    answers: List[AnswerSubmission]


class UserQuizResult(BaseModel):
    id: int
    user_id: int
    quiz_id: int
    score: int
    completed_at: datetime

    model_config = ConfigDict(from_attributes=True)