import logging
import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.api.endpoints import quiz, users, auth
from app.models.database import engine, Base, get_db
from app.models.user import User
from app.services.user_service import UserService
from app.config import settings

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A FastAPI application for hosting quiz competitions",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers from endpoints
app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["Authentication"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"])
app.include_router(quiz.router, prefix=f"{settings.API_V1_STR}/quiz", tags=["Quiz"])

@app.get("/")
async def root():
    """Root endpoint for health checking"""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "status": "running",
        "version": "1.0.0",
    }

@app.on_event("startup")
async def startup_event():
    """Startup event to initialize the application"""
    logger.info("Starting up Quiz Competition API")
    
    # Create the upload directory if it doesn't exist
    upload_directory = "uploads"
    if not os.path.exists(upload_directory):
        os.makedirs(upload_directory)
        logger.info(f"Created directory: {upload_directory}")
    else:
        logger.info(f"Directory already exists: {upload_directory}")

    # Additional startup logic can go here

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event"""
    logger.info("Shutting down Quiz Competition API")

