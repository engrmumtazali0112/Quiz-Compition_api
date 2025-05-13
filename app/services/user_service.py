from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status

from app.config import settings
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against the hashed version"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password for storage"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(
        data: dict, 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        """Create a new user"""
        # Hash the password
        hashed_password = UserService.get_password_hash(user.password)
        
        # Create user with hashed password
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            is_admin=user.is_admin if hasattr(user, 'is_admin') else False,
            full_name=user.full_name if hasattr(user, 'full_name') else None
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get a user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get a user by username"""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get a user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def update_user(db: Session, user_id: int, user: UserUpdate) -> Optional[User]:
        """Update a user"""
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            return None
        
        # Update user attributes excluding password
        update_data = user.dict(exclude_unset=True, exclude={"password"})
        for key, value in update_data.items():
            setattr(db_user, key, value)
        
        # If password is provided, update it
        if hasattr(user, "password") and user.password:
            db_user.hashed_password = UserService.get_password_hash(user.password)
        
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Delete a user"""
        db_user = UserService.get_user_by_id(db, user_id)
        if db_user:
            db.delete(db_user)
            db.commit()
            return True
        return False
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate a user by username and password"""
        user = UserService.get_user_by_username(db, username)
        if not user:
            return None
        if not UserService.verify_password(password, user.hashed_password):
            return None
        return user
    
    @staticmethod
    def get_user_statistics(db: Session, user_id: int) -> Dict[str, Any]:
        """Get statistics for a specific user"""
        from app.models.quiz import QuizAttempt
        
        # Get user
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            return {}
        
        # Total quizzes attempted
        total_attempts = db.query(QuizAttempt).filter(
            QuizAttempt.user_id == user_id,
            QuizAttempt.is_completed == True
        ).count()
        
        # Quizzes passed
        passed_attempts = db.query(QuizAttempt).filter(
            QuizAttempt.user_id == user_id,
            QuizAttempt.is_completed == True,
            QuizAttempt.passed == True
        ).count()
        
        # Average score
        avg_score = db.query(
            func.avg(QuizAttempt.score)
        ).filter(
            QuizAttempt.user_id == user_id,
            QuizAttempt.is_completed == True
        ).scalar() or 0
        
        # Recent attempts
        recent_attempts = db.query(
            QuizAttempt
        ).join(
            Quiz, QuizAttempt.quiz_id == Quiz.id
        ).filter(
            QuizAttempt.user_id == user_id,
            QuizAttempt.is_completed == True
        ).order_by(
            QuizAttempt.end_time.desc()
        ).limit(5).all()
        
        recent_attempt_data = []
        for attempt in recent_attempts:
            recent_attempt_data.append({
                "quiz_id": attempt.quiz_id,
                "quiz_title": attempt.quiz.title,
                "score": attempt.score,
                "passed": attempt.passed,
                "date": attempt.end_time
            })
        
        return {
            "user_id": user_id,
            "username": db_user.username,
            "total_attempts": total_attempts,
            "passed_attempts": passed_attempts,
            "pass_rate": (passed_attempts / total_attempts * 100) if total_attempts > 0 else 0,
            "average_score": avg_score,
            "recent_attempts": recent_attempt_data
        }
    
    @staticmethod
    def change_password(
        db: Session, 
        user_id: int, 
        current_password: str, 
        new_password: str
    ) -> bool:
        """Change a user's password"""
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            return False
        
        # Verify current password
        if not UserService.verify_password(current_password, db_user.hashed_password):
            return False
        
        # Update password
        db_user.hashed_password = UserService.get_password_hash(new_password)
        db.commit()
        return True