# Quiz Game API

## Overview

Welcome to the **Quiz Game API** project! This API is built with **FastAPI** and **PostgreSQL**, providing a backend for a quiz application where users can:
- Register and log in.
- Participate in quizzes.
- Track their quiz scores and results.

This project includes a frontend UI with animations that interacts with the backend API to create, submit, and view quizzes.

## Features

- **User Authentication**: Users can register, log in, and manage their profiles.
- **Quiz Management**: Users can create new quizzes, view available quizzes, and submit answers.
- **Leaderboard**: Users can view their scores and compare them with others.
- **Animations**: The frontend includes animations that make the user experience more interactive.

## Project Structure

quiz_app/
├── .env # Environment variables (configuration settings)
├── requirements.txt # Python dependencies
├── README.md # Project documentation
├── main.py # FastAPI application entry point
├── alembic/ # Database migrations
│ ├── env.py
│ ├── README
│ ├── script.py.mako
│ └── versions/
│ └── initial_migration.py
├── app/
│ ├── init.py
│ ├── api/
│ │ ├── init.py
│ │ ├── deps.py # Dependency injection
│ │ └── endpoints/
│ │ ├── init.py
│ │ ├── quiz.py # Quiz endpoints
│ │ └── user.py # User endpoints
│ ├── core/
│ │ ├── init.py
│ │ ├── config.py # Configuration settings
│ │ └── security.py # Security utilities
│ ├── db/
│ │ ├── init.py
│ │ ├── base.py # Base models
│ │ └── session.py # Database session
│ ├── models/
│ │ ├── init.py
│ │ ├── quiz.py # Quiz models
│ │ └── user.py # User models
│ ├── schemas/
│ │ ├── init.py
│ │ ├── quiz.py # Quiz schemas
│ │ └── user.py # User schemas
│ └── services/
│ ├── init.py
│ ├── quiz.py # Quiz business logic
│ └── user.py # User business logic
└── static/
├── css/
│ └── style.css # Styling for frontend
├── js/
│ └── script.js # Frontend interactivity
└── index.html # Frontend HTML with animations

markdown
Copy

## Technologies Used

- **FastAPI**: A modern Python web framework for building APIs quickly.
- **PostgreSQL**: A relational database for storing user data and quiz information.
- **SQLAlchemy**: ORM for database interaction.
- **JWT (JSON Web Tokens)**: Used for user authentication.
- **bcrypt**: Password hashing library.
- **Alembic**: Database migration tool for SQLAlchemy.
- **Frontend**: HTML, CSS, and JavaScript for the quiz game interface.
- **SweetAlert2**: Used for notifications in the frontend.

## Installation

### Prerequisites

- **Python 3.8+**
- **PostgreSQL**
- **pip** (Python's package installer)

### Step-by-step Installation:

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/your-username/quiz-game-api.git
   cd quiz-game-api
Set up the Virtual Environment:

It's recommended to use a virtual environment to manage dependencies.

bash
Copy
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
Install Dependencies:

Install the required Python packages:

bash
Copy
pip install -r requirements.txt
Configure the Database:

Make sure PostgreSQL is installed and running.

Create a new database quiz_db in PostgreSQL.

bash
Copy
psql -U postgres
CREATE DATABASE quiz_db;
Set up Environment Variables:

Rename .env.example to .env and configure the values inside (e.g., database URL, JWT secret key).

plaintext
Copy
DATABASE_URL="postgresql://postgres:your_password@localhost:5432/quiz_db"
SECRET_KEY=your_generated_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
Run Migrations:

If you're using Alembic for database migrations, run the following command to create the necessary tables:

bash
Copy
alembic upgrade head
Start the FastAPI Application:

Finally, start the FastAPI application using Uvicorn:

bash
Copy
uvicorn main:app --reload
The API should now be accessible at http://127.0.0.1:8000.

Test the API:




## Technologies Used

- **FastAPI**: A modern Python web framework for building APIs quickly.
- **PostgreSQL**: A relational database for storing user data and quiz information.
- **SQLAlchemy**: ORM for database interaction.
- **JWT (JSON Web Tokens)**: Used for user authentication.
- **bcrypt**: Password hashing library.
- **Alembic**: Database migration tool for SQLAlchemy.
- **Frontend**: HTML, CSS, and JavaScript for the quiz game interface.
- **SweetAlert2**: Used for notifications in the frontend.

## Installation

### Prerequisites

- **Python 3.8+**
- **PostgreSQL**
- **pip** (Python's package installer)

### Step-by-step Installation:

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/your-username/quiz-game-api.git
   cd quiz-game-api

```
quiz_app/
├── .env # Environment variables (configuration settings)
├── requirements.txt # Python dependencies
├── README.md # Project documentation
├── main.py # FastAPI application entry point
├── alembic/ # Database migrations
│ ├── env.py
│ ├── README
│ ├── script.py.mako
│ └── versions/
│ └── initial_migration.py
├── app/
│ ├── init.py
│ ├── api/
│ │ ├── init.py
│ │ ├── deps.py # Dependency injection
│ │ └── endpoints/
│ │ ├── init.py
│ │ ├── quiz.py # Quiz endpoints
│ │ └── user.py # User endpoints
│ ├── core/
│ │ ├── init.py
│ │ ├── config.py # Configuration settings
│ │ └── security.py # Security utilities
│ ├── db/
│ │ ├── init.py
│ │ ├── base.py # Base models
│ │ └── session.py # Database session
│ ├── models/
│ │ ├── init.py
│ │ ├── quiz.py # Quiz models
│ │ └── user.py # User models
│ ├── schemas/
│ │ ├── init.py
│ │ ├── quiz.py # Quiz schemas
│ │ └── user.py # User schemas
│ └── services/
│ ├── init.py
│ ├── quiz.py # Quiz business logic
│ └── user.py # User business logic
└── static/
├── css/
│ └── style.css # Styling for frontend
├── js/
│ └── script.js # Frontend interactivity
└── index.html # Frontend HTML with animations
```