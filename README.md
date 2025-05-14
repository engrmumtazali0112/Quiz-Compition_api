# 🎮 Quiz Game API

<div align="center">
  
  ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
  ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
  ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-CC2927?style=for-the-badge&logo=sqlalchemy&logoColor=white)
  ![JWT](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=JSON%20web%20tokens&logoColor=white)

  <p>A modern interactive quiz application with an animated frontend and robust API backend</p>
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  ![Version](https://img.shields.io/badge/version-0.1.0-blue)
  
</div>

## ✨ Overview

Welcome to the **Quiz Game API** project! This is a full-stack application built with **FastAPI** and **PostgreSQL** on the backend, featuring an animated and interactive frontend. The system allows users to register, create quizzes, participate in quizzes created by others, and track their scores on a leaderboard.

<div align="center">
  <img src="https://via.placeholder.com/800x400?text=Quiz+Game+Screenshot" alt="Quiz Game Screenshot" width="80%">
</div>

## 🚀 Features

- **👤 User Authentication**
  - Secure registration and login
  - JWT-based authentication
  - Password hashing with bcrypt
  
- **📝 Quiz Management**
  - Create custom quizzes with multiple-choice questions
  - View available quizzes from other users
  - Interactive quiz-taking interface
  
- **🏆 Results & Leaderboard**
  - Track personal quiz scores and history
  - Compare results with other users
  
- **🎭 User Experience**
  - Animated frontend interface
  - Responsive design for all devices
  - Intuitive navigation

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **PostgreSQL** - Reliable relational database
- **SQLAlchemy** - Powerful ORM for database interactions
- **Alembic** - Database migration tool
- **JWT** - Token-based authentication
- **bcrypt** - Secure password hashing

### Frontend
- **HTML5/CSS3/JavaScript** - Frontend fundamentals
- **Custom Animations** - Enhanced user experience
- **SweetAlert2** - Beautiful, responsive notifications

## 📋 Project Structure

```
quiz_app/
├── .env                  # Environment variables
├── requirements.txt      # Python dependencies
├── README.md             # Project documentation
├── main.py               # FastAPI application entry point
├── alembic/              # Database migrations
├── app/
│   ├── api/              # API endpoints
│   ├── core/             # Configuration and security
│   ├── db/               # Database setup
│   ├── models/           # Database models
│   ├── schemas/          # Pydantic schemas
│   └── services/         # Business logic
└── static/               # Frontend assets
    ├── css/              # Styling
    ├── js/               # Frontend interactivity
    └── index.html        # Main HTML template
```

## 🔧 Installation

### Prerequisites

- **Python 3.8+**
- **PostgreSQL**
- **Node.js** (optional, for frontend development)

### Step-by-Step Setup

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/quiz-game-api.git
cd quiz-game-api
```

2. **Set up a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure the database**

Create a PostgreSQL database:

```bash
psql -U postgres
CREATE DATABASE quiz_db;
```

5. **Set up environment variables**

Create a `.env` file with:

```
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/quiz_db
SECRET_KEY=your_generated_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

6. **Run database migrations**

```bash
alembic upgrade head
```

7. **Start the application**

```bash
uvicorn main:app --reload
```

The application will be available at `http://127.0.0.1:8000`

## 📝 API Documentation

Once the application is running, interactive API documentation is available at:

- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

## 📚 API Endpoints

### User Management
- `POST /api/users/register` - Register a new user
- `POST /api/users/token` - Login and get access token
- `GET /api/users/me` - Get current user details

### Quiz Operations
- `GET /api/quiz/` - List all available quizzes
- `POST /api/quiz/` - Create a new quiz
- `GET /api/quiz/{quiz_id}` - Get quiz details
- `POST /api/quiz/submit` - Submit quiz answers
- `GET /api/quiz/results/{quiz_id}` - Get results for a specific quiz
- `DELETE /api/quiz/{quiz_id}` - Delete a quiz (soft delete)

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication. To access protected endpoints:

1. Register a user or login to get a token
2. Include the token in requests using the `Authorization` header:
   ```
   Authorization: Bearer your_token_here
   ```

## 🖥️ Frontend

The application includes a built-in frontend accessible at the root URL (`http://127.0.0.1:8000`). The interface provides:

- User registration and login
- Quiz creation interface
- Quiz-taking experience with animations
- Results viewing

## 🧪 Testing

Run the test suite with:

```bash
pytest
```

## 📦 Dependencies

```
fastapi>=0.103.1
uvicorn>=0.23.2
sqlalchemy>=2.0.20
psycopg2-binary>=2.9.7
python-jose>=3.3.0
passlib>=1.7.4
python-multipart>=0.0.6
pydantic>=2.0.0
pydantic-settings>=2.0.0
alembic>=1.12.0
python-dotenv>=1.0.0
bcrypt>=4.0.1
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📬 Contact

Your Name - [@your_twitter](https://twitter.com/mali_yzi) - email@example.com

Project Link: [https://github.com/yourusername/quiz-game-api](https://github.com/engrmumtazali0112/Quiz-Compition_api)

---

<div align="center">
  <p>Made with Mumtaz Ali❤️ and ☕</p>
</div>