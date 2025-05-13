from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import get_user, get_optional_current_user
from app.schemas.token import TokenPayload

# Dependencies for database access
def get_db() -> Generator:
    """
    Dependency for getting the database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/users/token", 
    auto_error=False
)

# Dependency for getting current user
async def get_current_user(
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Get the current authenticated user.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user = get_user(db, user_id=token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user

# Dependency for getting current active user
async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get the current active authenticated user.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return current_user

# Dependency for getting current superuser
async def get_current_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get the current authenticated superuser.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user

# Dependency for getting optional current user (for endpoints that work with or without authentication)
async def get_optional_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[User]:
    """
    Get the current user if authenticated, None otherwise.
    """
    if not token:
        return None
    
    return await get_optional_current_user(token, db)