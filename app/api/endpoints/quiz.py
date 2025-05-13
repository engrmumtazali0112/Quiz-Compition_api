from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from app.api.dependencies import get_current_active_user, get_admin_user
from app.models.database import get_db
from app.models.user import User
from app.models.quiz import (
    Quiz, Question, Option, Category, 
    QuizQuestion, QuizAttempt, UserAnswer
)
from app.schemas.quiz import (
    Quiz as QuizSchema,
    QuizCreate, QuizUpdate, QuizDetail,
    Question as QuestionSchema,
    QuestionCreate, QuestionUpdate,
    Category as CategorySchema,
    CategoryCreate, CategoryUpdate,
    QuizAttempt as QuizAttemptSchema,
    QuizAttemptCreate, QuizAttemptUpdate,
    QuizAttemptDetail, QuizResult
)

router = APIRouter()

# Category endpoints
@router.post("/categories/", response_model=CategorySchema)
async def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    db_category = db.query(Category).filter(Category.name == category.name).first()
    if db_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category already exists"
        )
    
    db_category = Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    return db_category

@router.get("/categories/", response_model=List[CategorySchema])
async def get_categories(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    categories = db.query(Category).offset(skip).limit(limit).all()
    return categories

@router.get("/categories/{category_id}", response_model=CategorySchema)
async def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if db_category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return db_category

@router.put("/categories/{category_id}", response_model=CategorySchema)
async def update_category(
    category_id: int,
    category: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if db_category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    for key, value in category.dict(exclude_unset=True).items():
        setattr(db_category, key, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category

@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if db_category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    db.delete(db_category)
    db.commit()
    return None

# Question endpoints
@router.post("/questions/", response_model=QuestionSchema)
async def create_question(
    question: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    db_question = Question(
        text=question.text,
        difficulty=question.difficulty,
        category_id=question.category_id
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    
    # Add options
    for option in question.options:
        db_option = Option(
            text=option.text,
            is_correct=option.is_correct,
            question_id=db_question.id
        )
        db.add(db_option)
    
    db.commit()
    db.refresh(db_question)
    return db_question

@router.get("/questions/", response_model=List[QuestionSchema])
async def get_questions(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    difficulty: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Question)
    
    if category_id:
        query = query.filter(Question.category_id == category_id)
    
    if difficulty:
        query = query.filter(Question.difficulty == difficulty)
    
    questions = query.offset(skip).limit(limit).all()
    return questions

@router.get("/questions/{question_id}", response_model=QuestionSchema)
async def get_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_question = db.query(Question).filter(Question.id == question_id).first()
    if db_question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    return db_question

@router.put("/questions/{question_id}", response_model=QuestionSchema)
async def update_question(
    question_id: int,
    question: QuestionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    db_question = db.query(Question).filter(Question.id == question_id).first()
    if db_question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    # Update question attributes
    for key, value in question.dict(exclude={'options'}, exclude_unset=True).items():
        setattr(db_question, key, value)
    
    # Update options if provided
    if question.options:
        # Remove existing options
        db.query(Option).filter(Option.question_id == question_id).delete()
        
        # Add new options
        for option in question.options:
            db_option = Option(
                text=option.text,
                is_correct=option.is_correct,
                question_id=question_id
            )
            db.add(db_option)
    
    db.commit()
    db.refresh(db_question)
    return db_question

@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    db_question = db.query(Question).filter(Question.id == question_id).first()
    if db_question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    db.delete(db_question)
    db.commit()
    return None

# Quiz endpoints
@router.post("/quizzes/", response_model=QuizSchema)
async def create_quiz(
    quiz: QuizCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    db_quiz = Quiz(
        title=quiz.title,
        description=quiz.description,
        duration_minutes=quiz.duration_minutes,
        pass_percentage=quiz.pass_percentage,
        is_active=quiz.is_active,
        created_by=current_user.id
    )
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    
    # Add questions to quiz
    for question_id in quiz.question_ids:
        db_quiz_question = QuizQuestion(
            quiz_id=db_quiz.id,
            question_id=question_id
        )
        db.add(db_quiz_question)
    
    db.commit()
    db.refresh(db_quiz)
    return db_quiz

@router.get("/quizzes/", response_model=List[QuizSchema])
async def get_quizzes(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Quiz)
    
    if is_active is not None:
        query = query.filter(Quiz.is_active == is_active)
    
    quizzes = query.offset(skip).limit(limit).all()
    return quizzes

@router.get("/quizzes/{quiz_id}", response_model=QuizDetail)
async def get_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if db_quiz is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    return db_quiz

@router.put("/quizzes/{quiz_id}", response_model=QuizSchema)
async def update_quiz(
    quiz_id: int,
    quiz: QuizUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    db_quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if db_quiz is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    # Update quiz attributes
    for key, value in quiz.dict(exclude={'question_ids'}, exclude_unset=True).items():
        setattr(db_quiz, key, value)
    
    # Update questions if provided
    if quiz.question_ids:
        # Remove existing quiz questions
        db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz_id).delete()
        
        # Add new quiz questions
        for question_id in quiz.question_ids:
            db_quiz_question = QuizQuestion(
                quiz_id=quiz_id,
                question_id=question_id
            )
            db.add(db_quiz_question)
    
    db.commit()
    db.refresh(db_quiz)
    return db_quiz

@router.delete("/quizzes/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    db_quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if db_quiz is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    db.delete(db_quiz)
    db.commit()
    return None

# Quiz attempt endpoints
@router.post("/attempts/", response_model=QuizAttemptSchema)
async def create_quiz_attempt(
    attempt: QuizAttemptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check if quiz exists
    db_quiz = db.query(Quiz).filter(Quiz.id == attempt.quiz_id).first()
    if db_quiz is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    # Check if user has already attempted this quiz
    existing_attempt = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == attempt.quiz_id,
        QuizAttempt.user_id == current_user.id,
        QuizAttempt.is_completed == True
    ).first()
    
    if existing_attempt and not db_quiz.allow_multiple_attempts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already attempted this quiz"
        )
    
    # Create new attempt
    db_attempt = QuizAttempt(
        quiz_id=attempt.quiz_id,
        user_id=current_user.id,
        start_time=datetime.now(),
        is_completed=False
    )
    
    db.add(db_attempt)
    db.commit()
    db.refresh(db_attempt)
    return db_attempt

@router.get("/attempts/", response_model=List[QuizAttemptSchema])
async def get_quiz_attempts(
    quiz_id: Optional[int] = None,
    is_completed: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(QuizAttempt).filter(QuizAttempt.user_id == current_user.id)
    
    if quiz_id:
        query = query.filter(QuizAttempt.quiz_id == quiz_id)
    
    if is_completed is not None:
        query = query.filter(QuizAttempt.is_completed == is_completed)
    
    attempts = query.all()
    return attempts

@router.get("/attempts/{attempt_id}", response_model=QuizAttemptDetail)
async def get_quiz_attempt(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_attempt = db.query(QuizAttempt).filter(
        QuizAttempt.id == attempt_id,
        QuizAttempt.user_id == current_user.id
    ).first()
    
    if db_attempt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz attempt not found"
        )
    
    return db_attempt

@router.post("/attempts/{attempt_id}/submit", response_model=QuizResult)
async def submit_quiz_attempt(
    attempt_id: int,
    answers: List[QuizAttemptUpdate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Get the attempt
    db_attempt = db.query(QuizAttempt).filter(
        QuizAttempt.id == attempt_id,
        QuizAttempt.user_id == current_user.id
    ).first()
    
    if db_attempt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz attempt not found"
        )
    
    if db_attempt.is_completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quiz attempt already completed"
        )
    
    # Get quiz
    db_quiz = db.query(Quiz).filter(Quiz.id == db_attempt.quiz_id).first()
    
    # Save user answers
    for answer in answers:
        # Check if option exists and belongs to the quiz
        option = db.query(Option).join(Question).join(
            QuizQuestion, Question.id == QuizQuestion.question_id
        ).filter(
            QuizQuestion.quiz_id == db_attempt.quiz_id,
            Option.id == answer.option_id
        ).first()
        
        if option is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid option ID: {answer.option_id}"
            )
        
        # Save answer
        db_answer = UserAnswer(
            attempt_id=attempt_id,
            question_id=option.question_id,
            option_id=option.id
        )
        db.add(db_answer)
    
    # Calculate score
    total_questions = db.query(QuizQuestion).filter(
        QuizQuestion.quiz_id == db_attempt.quiz_id
    ).count()
    
    correct_answers = db.query(UserAnswer).join(
        Option, UserAnswer.option_id == Option.id
    ).filter(
        UserAnswer.attempt_id == attempt_id,
        Option.is_correct == True
    ).count()
    
    score_percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    passed = score_percentage >= db_quiz.pass_percentage
    
    # Update attempt as completed
    db_attempt.end_time = datetime.now()
    db_attempt.score = score_percentage
    db_attempt.is_completed = True
    db_attempt.passed = passed
    
    db.commit()
    
    return QuizResult(
        attempt_id=attempt_id,
        quiz_id=db_attempt.quiz_id,
        total_questions=total_questions,
        correct_answers=correct_answers,
        score_percentage=score_percentage,
        passed=passed,
        completion_time=db_attempt.end_time
    )

# Admin endpoints for analytics
@router.get("/analytics/quiz/{quiz_id}", response_model=dict)
async def get_quiz_analytics(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    # Check if quiz exists
    db_quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if db_quiz is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    # Get total attempts
    total_attempts = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.is_completed == True
    ).count()
    
    # Get pass rate
    passed_attempts = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.is_completed == True,
        QuizAttempt.passed == True
    ).count()
    
    pass_rate = (passed_attempts / total_attempts) * 100 if total_attempts > 0 else 0
    
    # Get average score
    avg_score = db.query(func.avg(QuizAttempt.score)).filter(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.is_completed == True
    ).scalar() or 0
    
    # Get question-level analytics
    questions = db.query(Question).join(
        QuizQuestion, Question.id == QuizQuestion.question_id
    ).filter(
        QuizQuestion.quiz_id == quiz_id
    ).all()
    
    question_stats = []
    for question in questions:
        # Count how many times this question was answered correctly
        correct_count = db.query(UserAnswer).join(
            QuizAttempt, UserAnswer.attempt_id == QuizAttempt.id
        ).join(
            Option, UserAnswer.option_id == Option.id
        ).filter(
            QuizAttempt.quiz_id == quiz_id,
            UserAnswer.question_id == question.id,
            Option.is_correct == True
        ).count()
        
        # Count total attempts for this question
        total_question_attempts = db.query(UserAnswer).join(
            QuizAttempt, UserAnswer.attempt_id == QuizAttempt.id
        ).filter(
            QuizAttempt.quiz_id == quiz_id,
            UserAnswer.question_id == question.id
        ).count()
        
        correct_rate = (correct_count / total_question_attempts) * 100 if total_question_attempts > 0 else 0
        
        question_stats.append({
            "question_id": question.id,
            "text": question.text,
            "correct_rate": correct_rate
        })
    
    return {
        "quiz_id": quiz_id,
        "title": db_quiz.title,
        "total_attempts": total_attempts,
        "pass_rate": pass_rate,
        "average_score": avg_score,
        "question_stats": question_stats
    }

@router.get("/leaderboard/{quiz_id}", response_model=List[dict])
async def get_quiz_leaderboard(
    quiz_id: int,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check if quiz exists
    db_quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if db_quiz is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    # Get top scores
    top_scores = db.query(
        QuizAttempt.user_id,
        User.username,
        func.max(QuizAttempt.score).label("score"),
        func.min(func.extract('epoch', QuizAttempt.end_time) - 
                func.extract('epoch', QuizAttempt.start_time)).label("time_taken")
    ).join(
        User, QuizAttempt.user_id == User.id
    ).filter(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.is_completed == True
    ).group_by(
        QuizAttempt.user_id, User.username
    ).order_by(
        func.max(QuizAttempt.score).desc(),
        func.min(func.extract('epoch', QuizAttempt.end_time) - 
                func.extract('epoch', QuizAttempt.start_time)).asc()
    ).limit(limit).all()
    
    leaderboard = []
    for i, (user_id, username, score, time_taken) in enumerate(top_scores, start=1):
        leaderboard.append({
            "rank": i,
            "user_id": user_id,
            "username": username,
            "score": score,
            "time_taken_seconds": time_taken
        })
    
    return leaderboard