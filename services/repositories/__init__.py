# Repository layer for data access
from .user_repository import UserRepository
from .question_repository import QuestionRepository
from .answer_repository import AnswerRepository

# Create singleton instances
user_repository = UserRepository()

# Lazy initialization functions for repositories that need database sessions
def get_question_repository():
    from services.database import SessionLocal
    db = SessionLocal()
    return QuestionRepository(db)

def get_answer_repository():
    from services.database import SessionLocal
    db = SessionLocal()
    return AnswerRepository(db)

# For compatibility with existing code
def get_user_repository():
    return user_repository

__all__ = [
    "UserRepository",
    "QuestionRepository", 
    "AnswerRepository",
    "user_repository",
    "get_user_repository",
    "get_question_repository",
    "get_answer_repository"
]
