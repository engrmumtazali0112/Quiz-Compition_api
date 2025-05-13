from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text, nullable=True)
    
    # Relationships
    questions = relationship("Question", back_populates="category")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    difficulty = Column(Integer, default=1)  # 1-5 scale
    explanation = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    
    # Relationships
    category = relationship("Category", back_populates="questions")
    options = relationship("Option", back_populates="question", cascade="all, delete-orphan")
    quiz_questions = relationship("QuizQuestion", back_populates="question")


class Option(Base):
    __tablename__ = "options"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)
    question_id = Column(Integer, ForeignKey("questions.id"))
    
    # Relationships
    question = relationship("Question", back_populates="options")


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    time_limit = Column(Integer, nullable=True)  # Time limit in seconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    creator = relationship("User", back_populates="created_quizzes")
    quiz_questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    order = Column(Integer, default=0)
    
    # Relationships
    quiz = relationship("Quiz", back_populates="quiz_questions")
    question = relationship("Question", back_populates="quiz_questions")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    score = Column(Float, nullable=True)
    
    # Relationships
    quiz = relationship("Quiz", back_populates="attempts")
    user = relationship("User", back_populates="quiz_attempts")
    answers = relationship("UserAnswer", back_populates="attempt", cascade="all, delete-orphan")


class UserAnswer(Base):
    __tablename__ = "user_answers"

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("quiz_attempts.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    selected_option_id = Column(Integer, ForeignKey("options.id"), nullable=True)
    is_correct = Column(Boolean, nullable=True)
    time_taken = Column(Float, nullable=True)  # Time in seconds
    
    # Relationships
    attempt = relationship("QuizAttempt", back_populates="answers")
    question = relationship("Question")
    selected_option = relationship("Option")