from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.quiz import Quiz, Question, Answer, UserQuizResult
from app.models.user import User
from app.schemas.quiz import (
    Quiz as QuizSchema,
    QuizCreate,
    UserQuizResult as UserQuizResultSchema,
    QuizSubmission,
)

router = APIRouter()

@router.post("/", response_model=QuizSchema)
def create_quiz(
    quiz_in: QuizCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create new quiz.
    """
    quiz = Quiz(
        title=quiz_in.title,
        description=quiz_in.description,
        created_by=current_user.id,
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    
    # Add questions and answers
    for q_idx, q_data in enumerate(quiz_in.questions):
        question = Question(
            quiz_id=quiz.id,
            text=q_data.text,
            order=q_data.order or q_idx,
        )
        db.add(question)
        db.commit()
        db.refresh(question)
        
        # Add answers for this question
        for a_data in q_data.answers:
            answer = Answer(
                question_id=question.id,
                text=a_data.text,
                is_correct=a_data.is_correct,
            )
            db.add(answer)
        
    db.commit()
    db.refresh(quiz)
    return quiz

@router.get("/", response_model=List[QuizSchema])
def read_quizzes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Retrieve quizzes.
    """
    quizzes = db.query(Quiz).filter(Quiz.is_active == True).offset(skip).limit(limit).all()
    return quizzes

@router.get("/{quiz_id}", response_model=QuizSchema)
def read_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get quiz by ID.
    """
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.is_active == True).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz

@router.post("/submit", response_model=UserQuizResultSchema)
def submit_quiz(
    submission: QuizSubmission,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Submit quiz answers and get results.
    """
    # Check if quiz exists
    quiz = db.query(Quiz).filter(Quiz.id == submission.quiz_id, Quiz.is_active == True).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Calculate score
    total_questions = len(quiz.questions)
    correct_answers = 0
    
    answer_map = {answer.question_id: answer.answer_id for answer in submission.answers}
    
    for question in quiz.questions:
        submitted_answer_id = answer_map.get(question.id)
        if submitted_answer_id:
            is_correct = db.query(Answer).filter(
                Answer.id == submitted_answer_id,
                Answer.question_id == question.id,
                Answer.is_correct == True
            ).first() is not None
            
            if is_correct:
                correct_answers += 1
    
    # Calculate percentage score
    score = int((correct_answers / total_questions) * 100) if total_questions > 0 else 0
    
    # Save results
    quiz_result = UserQuizResult(
        user_id=current_user.id,
        quiz_id=quiz.id,
        score=score,
    )
    db.add(quiz_result)
    db.commit()
    db.refresh(quiz_result)
    
    return quiz_result

@router.get("/results/{quiz_id}", response_model=List[UserQuizResultSchema])
def read_quiz_results(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get user's results for a specific quiz.
    """
    results = db.query(UserQuizResult).filter(
        UserQuizResult.quiz_id == quiz_id,
        UserQuizResult.user_id == current_user.id
    ).all()
    
    return results

@router.delete("/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Delete a quiz.
    """
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    if quiz.created_by != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Soft delete
    quiz.is_active = False
    db.commit()
    return None  # Ensure no body is returned for status code 204.
   