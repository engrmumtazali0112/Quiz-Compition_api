
#Install Postgre SQL version https://www.enterprisedb.com/downloads/postgres-postgresql-downloads

quiz_app/
├── .env                       # Environment variables
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
├── main.py                    # FastAPI application entry point
├── alembic/                   # Database migrations
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   └── versions/
│       └── initial_migration.py
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py            # Dependency injection
│   │   └── endpoints/
│   │       ├── __init__.py
│   │       ├── quiz.py        # Quiz endpoints
│   │       └── user.py        # User endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration settings
│   │   └── security.py        # Security utilities
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py            # Base models
│   │   └── session.py         # Database session
│   ├── models/
│   │   ├── __init__.py
│   │   ├── quiz.py            # Quiz models
│   │   └── user.py            # User models
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── quiz.py            # Quiz schemas
│   │   └── user.py            # User schemas
│   └── services/
│       ├── __init__.py
│       ├── quiz.py            # Quiz business logic
│       └── user.py            # User business logic
└── static/
    ├── css/
    │   └── style.css
    ├── js/
    │   └── script.js
    └── index.html            # Simple frontend