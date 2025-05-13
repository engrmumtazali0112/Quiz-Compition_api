from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.models.quiz import (
    Quiz, Question, Option, Category, 
    QuizQuestion, QuizAttempt, UserAnswer
)
from app.models.user import User
from app.schemas.quiz import (
    QuizCreate, QuizUpdate,
    QuestionCreate, QuestionUpdate,
    CategoryCreate, CategoryUpdate,
    QuizAttemptCreate
)


class QuizService:
    @staticmethod
    def create_category(db: Session, category: CategoryCreate) -> Category:
        """Create a new category"""
        db_category = Category(**category.dict())
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    
    @staticmethod
    def get_categories(db: Session, skip: int = 0, limit: int = 100) -> List[Category]:
        """Get all categories with pagination"""
        return db.query(Category).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_category_by_id(db: Session, category_id: int) -> Optional[Category]:
        """Get a category by ID"""
        return db.query(Category).filter(Category.id == category_id).first()
    
    @staticmethod
    def get_category_by_name(db: Session, name: str) -> Optional[Category]:
        """Get a category by name"""
        return db.query(Category).filter(Category.name == name).first()
    
    @staticmethod
    def update_category(db: Session, category_id: int, category: CategoryUpdate) -> Optional[Category]:
        """Update a category"""
        db_category = QuizService.get_category_by_id(db, category_id)
        if db_category:
            for key, value in category.dict(exclude_unset=True).items():
                setattr(db_category, key, value)
            db.commit()
            db.refresh(db_category)
        return db_category
    
    @staticmethod
    def delete_category(db: Session, category_id: int) -> bool:
        """Delete a category"""
        db_category = QuizService.get_category_by_id(db, category_id)
        if db_category:
            db.delete(db_category)
            db.commit()
            return True
        return False
    
    @staticmethod
    def create_question(db: Session, question: QuestionCreate) -> Question:
        """Create a new question with options"""
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
    
    @staticmethod
    def get_questions(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        category_id: Optional[int] = None,
        difficulty: Optional[str] = None
    ) -> List[Question]:
        """Get questions with filters and pagination"""
        query = db.query(Question)
        
        if category_id:
            query = query.filter(Question.category_id == category_id)
        
        if difficulty:
            query = query.filter(Question.difficulty == difficulty)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_question_by_id(db: Session, question_id: int) -> Optional[Question]:
        """Get a question by ID"""
        return db.query(Question).filter(Question.id == question_id).first()
    
    @staticmethod
    def update_question(db: Session, question_id: int, question: QuestionUpdate) -> Optional[Question]:
        """Update a question and its options"""
        db_question = QuizService.get_question_by_id(db, question_id)
        if not db_question:
            return None
        
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
    
    @staticmethod
    def delete_question(db: Session, question_id: int) -> bool:
        """Delete a question"""
        db_question = QuizService.get_question_by_id(db, question_id)
        if db_question:
            db.delete(db_question)
            db.commit()
            return True
        return False
    
    @staticmethod
    def create_quiz(db: Session, quiz: QuizCreate, user_id: int) -> Quiz:
        """Create a new quiz with questions"""
        db_quiz = Quiz(
            title=quiz.title,
            description=quiz.description,
            duration_minutes=quiz.duration_minutes,
            pass_percentage=quiz.pass_percentage,
            is_active=quiz.is_active,
            allow_multiple_attempts=quiz.allow_multiple_attempts,
            created_by=user_id
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
    
    @staticmethod
    def get_quizzes(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[Quiz]:
        """Get quizzes with filters and pagination"""
        query = db.query(Quiz)
        
        if is_active is not None:
            query = query.filter(Quiz.is_active == is_active)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_quiz_by_id(db: Session, quiz_id: int) -> Optional[Quiz]:
        """Get a quiz by ID"""
        return db.query(Quiz).filter(Quiz.id == quiz_id).first()
    
    @staticmethod
    def update_quiz(db: Session, quiz_id: int, quiz: QuizUpdate) -> Optional[Quiz]:
        """Update a quiz and its questions"""
        db_quiz = QuizService.get_quiz_by_id(db, quiz_id)
        if not db_quiz:
            return None
        
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
    
    @staticmethod
    def delete_quiz(db: Session, quiz_id: int) -> bool:
        """Delete a quiz"""
        db_quiz = QuizService.get_quiz_by_id(db, quiz_id)
        if db_quiz:
            db.delete(db_quiz)
            db.commit()
            return True
        return False
    
    @staticmethod
    def create_quiz_attempt(db: Session, attempt: QuizAttemptCreate, user_id: int) -> QuizAttempt:
        """Create a new quiz attempt"""
        db_attempt = QuizAttempt(
            quiz_id=attempt.quiz_id,
            user_id=user_id,
            start_time=datetime.now(),
            is_completed=False
        )
        
        db.add(db_attempt)
        db.commit()
        db.refresh(db_attempt)
        return db_attempt
    
    @staticmethod
    def get_quiz_attempts(
        db: Session, 
        user_id: int,
        quiz_id: Optional[int] = None,
        is_completed: Optional[bool] = None
    ) -> List[QuizAttempt]:
        """Get quiz attempts with filters"""
        query = db.query(QuizAttempt).filter(QuizAttempt.user_id == user_id)
        
        if quiz_id:
            query = query.filter(QuizAttempt.quiz_id == quiz_id)
        
        if is_completed is not None:
            query = query.filter(QuizAttempt.is_completed == is_completed)
        
        return query.all()
    
    @staticmethod
    def get_quiz_attempt_by_id(db: Session, attempt_id: int, user_id: int) -> Optional[QuizAttempt]:
        """Get a quiz attempt by ID for a specific user"""
        return db.query(QuizAttempt).filter(
            QuizAttempt.id == attempt_id,
            QuizAttempt.user_id == user_id
        ).first()
    
    @staticmethod
    def submit_quiz_answers(
        db: Session, 
        attempt_id: int, 
        user_answers: List[Dict[str, int]]
    ) -> Optional[Dict[str, Any]]:
        """Submit quiz answers and calculate results"""
        # Get the attempt
        db_attempt = db.query(QuizAttempt).filter(
            QuizAttempt.id == attempt_id
        ).first()
        
        if not db_attempt or db_attempt.is_completed:
            return None
        
        # Get quiz
        db_quiz = db.query(Quiz).filter(Quiz.id == db_attempt.quiz_id).first()
        
        # Save user answers
        for answer in user_answers:
            # Check if option exists and belongs to the quiz
            option = db.query(Option).join(Question).join(
                QuizQuestion, Question.id == QuizQuestion.question_id
            ).filter(
                QuizQuestion.quiz_id == db_attempt.quiz_id,
                Option.id == answer["option_id"]
            ).first()
            
            if option:
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
        
        return {
            "attempt_id": attempt_id,
            "quiz_id": db_attempt.quiz_id,
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "score_percentage": score_percentage,
            "passed": passed,
            "completion_time": db_attempt.end_time
        }
    
    @staticmethod
    def get_quiz_analytics(db: Session, quiz_id: int) -> Dict[str, Any]:
        """Get analytics for a specific quiz"""
        # Check if quiz exists
        db_quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
        if not db_quiz:
            return {}
        
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
    
    @staticmethod
    def get_quiz_leaderboard(db: Session, quiz_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get leaderboard for a specific quiz"""
        # Check if quiz exists
        db_quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
        if not db_quiz:
            return []
        
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
    
    @staticmethod
    def get_random_questions(
        db: Session, 
        category_id: Optional[int] = None,
        difficulty: Optional[str] = None,
        count: int = 10
    ) -> List[Question]:
        """Get random questions for quiz creation"""
        query = db.query(Question)
        
        if category_id:
            query = query.filter(Question.category_id == category_id)
        
        if difficulty:
            query = query.filter(Question.difficulty == difficulty)
        
        # Use random order and limit
        return query.order_by(func.random()).limit(count).all()