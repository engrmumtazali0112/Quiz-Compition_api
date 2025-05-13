from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import quiz, user
from app.core.config import settings
from app.db.session import engine
from app.db.base_class import Base 

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Quiz Game API",
    description="A simple quiz game API built with FastAPI and PostgreSQL",
    version="0.1.0",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(quiz.router, prefix="/api/quiz", tags=["quiz"])
app.include_router(user.router, prefix="/api/users", tags=["users"])

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "Welcome to the Quiz Game API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)