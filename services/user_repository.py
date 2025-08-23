from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.user import User
from services.database import SessionLocal


class UserRepository:
    def __init__(self):
        pass

    def get_db(self) -> Session:
        db = SessionLocal()
        try:
            return db
        finally:
            pass

    def create_user(self, user_data: dict) -> tuple[Optional[User], Optional[str]]:
        db = self.get_db()
        try:
            user = User(**user_data)
            db.add(user)
            db.commit()
            db.refresh(user)
            return user, None
        except IntegrityError as e:
            db.rollback()
            if "email" in str(e):
                return None, "Email already exists"
            elif "phone_number" in str(e):
                return None, "Phone number already exists"
            else:
                return None, "User data conflict"
        except Exception as e:
            db.rollback()
            return None, f"Database error: {str(e)}"
        finally:
            db.close()

    def get_user_by_email(self, email: str) -> Optional[User]:
        db = self.get_db()
        try:
            return db.query(User).filter(User.email == email).first()
        except Exception:
            return None
        finally:
            db.close()

    def get_user_by_phone(self, phone_number: str) -> Optional[User]:
        db = self.get_db()
        try:
            return db.query(User).filter(User.phone_number == phone_number).first()
        except Exception:
            return None
        finally:
            db.close()

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        db = self.get_db()
        try:
            return db.query(User).filter(User.id == user_id).first()
        except Exception:
            return None
        finally:
            db.close()

    def update_user(self, user_id: str, update_data: dict) -> tuple[Optional[User], Optional[str]]:
        db = self.get_db()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None, "User not found"
            
            for key, value in update_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            db.commit()
            db.refresh(user)
            return user, None
        except IntegrityError as e:
            db.rollback()
            if "email" in str(e):
                return None, "Email already exists"
            elif "phone_number" in str(e):
                return None, "Phone number already exists"
            else:
                return None, "Data conflict"
        except Exception as e:
            db.rollback()
            return None, f"Database error: {str(e)}"
        finally:
            db.close()

    def delete_user(self, user_id: str) -> tuple[bool, Optional[str]]:
        db = self.get_db()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False, "User not found"
            
            db.delete(user)
            db.commit()
            return True, None
        except Exception as e:
            db.rollback()
            return False, f"Database error: {str(e)}"
        finally:
            db.close()


user_repository = UserRepository()