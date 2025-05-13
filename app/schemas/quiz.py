from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


# Option schemas
class OptionBase(BaseModel):
    text: str
    is_correct: bool


class OptionCreate(OptionBase):
    pass


class OptionUpdate(OptionBase):
    pass


class Option(OptionBase):
    id: int
    question_id: int
    
    class Config:
        orm_mode = True


# Question schemas
class QuestionBase(BaseModel):
    text: str
    difficulty: int = Field(1, ge=1, le=5)
    explanation: Optional[str] = None
    category_id: int


class QuestionCreate(QuestionBase):
    options: List[OptionCreate]


class QuestionUpdate(QuestionBase):
    options: Optional[List[OptionCreate]] = None


class Question(QuestionBase):
    id: int
    options: List[Option]
    
    class Config:
        orm_mode = True


class QuestionWithoutCorrectAnswer(BaseModel):
    id: int
    text: str
    difficulty: int
    category_id: int
    options: List[BaseModel]
    
    class Config:
        orm_mode = True


# Category schemas
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int
    
    class Config:
        orm_mode = True


# Quiz schemas
class QuizBase(BaseModel):
    title: str
    description: Optional[str] = None
    time_limit: Optional[int] = None  # Time limit in seconds


class QuizCreate(QuizBase):
    question_ids: List[int]


class QuizUpdate(QuizBase):
    is_active: Optional[bool] = None
    question_ids: Optional[List[int]] = None


class Quiz(QuizBase):
    id: int
    created_at: datetime
    is_active: bool
    created_by: int
    
    class Config:
        orm_mode = True


class QuizDetail(Quiz):
    questions: List[Question]
    
    class Config:
        orm_mode = True


# Quiz attempt schemas
class UserAnswerCreate(BaseModel):
    question_id: int
    selected_option_id: Optional[int] = None
    time_taken: Optional[float] = None


class UserAnswer(UserAnswerCreate):
    id: int
    is_correct: Optional[bool] = None
    
    class Config:
        orm_mode = True


class QuizAttemptBase(BaseModel):
    quiz_id: int


class QuizAttemptCreate(QuizAttemptBase):
    pass


class QuizAttemptUpdate(BaseModel):
    answers: List[UserAnswerCreate]


class QuizAttempt(QuizAttemptBase):
    id: int
    user_id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    score: Optional[float] = None
    
    class Config:
        orm_mode = True


class QuizAttemptDetail(QuizAttempt):
    answers: List[UserAnswer]
    
    class Config:
        orm_mode = True


class QuizResult(BaseModel):
    attempt_id: int
    quiz_id: int
    score: float
    total_questions: int
    correct_answers: int
    time_taken: float  # In seconds
    completed_at: datetime