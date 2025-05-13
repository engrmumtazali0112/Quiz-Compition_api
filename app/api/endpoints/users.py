from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.dependencies import get_current_active_user, get_admin_user
from app.api.endpoints.auth import get_password_hash
from app.models.database import get_db
from app.models.user import User
from app.models.quiz import QuizAttempt, Quiz
from app.schemas.user import User as UserSchema, UserUpdate, UserProfile

router = APIRouter()


@router.get("/me", response_model=UserSchema)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.get("/me/profile", response_model=UserProfile)
async def read_user_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get total quizzes taken
    total_quizzes_taken = db.query(func.count(QuizAttempt.id))\
        .filter(QuizAttempt.user_id == current_user.id)\
        .scalar()
    
    # Get total quizzes created
    quizzes_created = db.query(func.count(Quiz.id))\
        .filter(Quiz.created_by == current_user.id)\
        .scalar()
    
    # Get average score
    average_score_query = db.query(func.avg(QuizAttempt.score))\
        .filter(
            QuizAttempt.user_id == current_user.id,
            QuizAttempt.completed_at.isnot(None)
        )\
        .scalar()
    
    average_score = float(average_score_query) if average_score_query else None
    
    return {
        "user": current_user,
        "total_quizzes_taken": total_quizzes_taken,
        "quizzes_created": quizzes_created,
        "average_score": average_score
    }


@router.put("/me", response_model=UserSchema)
async def update_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Update user fields if provided
    if user_update.email is not None:
        # Check if email already exists
        db_user = db.query(User).filter(User.email == user_update.email).first()
        if db_user and db_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        current_user.email = user_update.email
    
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    
    if user_update.password is not None:
        current_user.hashed_password = get_password_hash(user_update.password)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.get("/", response_model=List[UserSchema], dependencies=[Depends(get_admin_user)])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserSchema, dependencies=[Depends(get_admin_user)])
async def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user