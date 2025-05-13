from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException

from app.models.user import User
from app.models.quiz import Quiz, Question, Answer, QuizResult
from app.schemas.quiz import (
    QuizCreate, 
    QuestionCreate, 
    AnswerCreate, 
    QuizSubmission, 
    QuizWithQuestions
)

# Quiz CRUD operations
def get_quizzes(db: Session, skip: int = 0, limit: int = 100) -> List[Quiz]:
    return db.query(Quiz).order_by(desc(Quiz.created_at)).offset(skip).limit(limit).all()

def get_quiz(db: Session, quiz_id: int) -> Optional[Quiz]:
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz

def get_quiz_with_questions(db: Session, quiz_id: int) -> QuizWithQuestions:
    quiz = get_quiz(db, quiz_id)
    
    # Eager load questions and answers
    questions = db.query(Question).filter(Question.quiz_id == quiz_id).all()
    
    # Format as QuizWithQuestions schema
    quiz_with_questions = QuizWithQuestions(
        id=quiz.id,
        title=quiz.title,
        description=quiz.description,
        created_at=quiz.created_at,
        user_id=quiz.user_id,
        questions=[]
    )
    
    for question in questions:
        answers = db.query(Answer).filter(Answer.question_id == question.id).all()
        
        question_dict = {
            "id": question.id,
            "text": question.text,
            "answers": []
        }
        
        for answer in answers:
            answer_dict = {
                "id": answer.id,
                "text": answer.text,
                "is_correct": answer.is_correct
            }
            question_dict["answers"].append(answer_dict)
        
        quiz_with_questions.questions.append(question_dict)
    
    return quiz_with_questions

def create_quiz(db: Session, quiz_create: QuizCreate, user_id: int) -> Quiz:
    # Create quiz
    db_quiz = Quiz(
        title=quiz_create.title,
        description=quiz_create.description,
        user_id=user_id
    )
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    
    # Create questions and answers
    for question_create in quiz_create.questions:
        db_question = Question(
            text=question_create.text,
            quiz_id=db_quiz.id
        )
        db.add(db_question)
        db.commit()
        db.refresh(db_question)
        
        for answer_create in question_create.answers:
            db_answer = Answer(
                text=answer_create.text,
                is_correct=answer_create.is_correct,
                question_id=db_question.id
            )
            db.add(db_answer)
    
    db.commit()
    return db_quiz

def update_quiz(db: Session, quiz_id: int, quiz_update: QuizCreate, user_id: int) -> Quiz:
    db_quiz = get_quiz(db, quiz_id)
    
    # Check if user is the owner of the quiz
    if db_quiz.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Update quiz attributes
    for key, value in quiz_update.dict(exclude={"questions"}).items():
        setattr(db_quiz, key, value)
    
    # Remove existing questions and answers
    questions = db.query(Question).filter(Question.quiz_id == quiz_id).all()
    for question in questions:
        db.query(Answer).filter(Answer.question_id == question.id).delete()
    db.query(Question).filter(Question.quiz_id == quiz_id).delete()
    
    # Create new questions and answers
    for question_create in quiz_update.questions:
        db_question = Question(
            text=question_create.text,
            quiz_id=db_quiz.id
        )
        db.add(db_question)
        db.commit()
        db.refresh(db_question)
        
        for answer_create in question_create.answers:
            db_answer = Answer(
                text=answer_create.text,
                is_correct=answer_create.is_correct,
                question_id=db_question.id
            )
            db.add(db_answer)
    
    db.commit()
    db.refresh(db_quiz)
    return db_quiz

def delete_quiz(db: Session, quiz_id: int, user_id: int) -> Dict[str, str]:
    db_quiz = get_quiz(db, quiz_id)
    
    # Check if user is the owner of the quiz
    if db_quiz.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Delete related questions and answers
    questions = db.query(Question).filter(Question.quiz_id == quiz_id).all()
    for question in questions:
        db.query(Answer).filter(Answer.question_id == question.id).delete()
    db.query(Question).filter(Question.quiz_id == quiz_id).delete()
    
    # Delete quiz
    db.delete(db_quiz)
    db.commit()
    
    return {"message": "Quiz deleted successfully"}

def submit_quiz(db: Session, quiz_id: int, submission: QuizSubmission, user_id: int) -> Dict[str, Any]:
    quiz = get_quiz(db, quiz_id)
    
    # Get all questions for this quiz
    questions = db.query(Question).filter(Question.quiz_id == quiz_id).all()
    
    # Validate all questions were answered
    if len(submission.answers) != len(questions):
        raise HTTPException(status_code=400, detail="All questions must be answered")
    
    # Calculate score
    total_questions = len(questions)
    correct_answers = 0
    
    for answer_submission in submission.answers:
        # Get correct answer for this question
        correct_answer = db.query(Answer).filter(
            Answer.question_id == answer_submission.question_id,
            Answer.is_correct == True
        ).first()
        
        if not correct_answer:
            raise HTTPException(status_code=500, detail="Question has no correct answer")
        
        if answer_submission.answer_id == correct_answer.id:
            correct_answers += 1
    
    score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    
    # Save quiz result
    quiz_result = QuizResult(
        quiz_id=quiz_id,
        user_id=user_id,
        score=score
    )
    db.add(quiz_result)
    db.commit()
    db.refresh(quiz_result)
    
    return {
        "quiz_id": quiz_id,
        "user_id": user_id,
        "score": score,
        "correct_answers": correct_answers,
        "total_questions": total_questions
    }

def get_user_quiz_results(db: Session, user_id: int) -> List[QuizResult]:
    return db.query(QuizResult).filter(QuizResult.user_id == user_id).all()