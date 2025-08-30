from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from models.domain.user import User
from services.database import SessionLocal
import json


class UserRepository:
    def __init__(self):
        pass

    def get_db(self) -> Session:
        return SessionLocal()
    def find_user_by_oauth(self, provider: str, provider_id: str) -> Optional[User]:
        db = self.get_db()
        try:
            return db.query(User).filter(
                User.oauth_provider == provider,
                User.oauth_provider_id == provider_id
            ).first()
        except Exception:
            return None
        finally:
            db.close()    


            
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

    def get_user_by_oauth(self, provider: str, provider_id: str) -> Optional[User]:
        db = self.get_db()
        try:
            return db.query(User).filter(
                User.oauth_provider == provider,
                User.oauth_provider_id == provider_id
            ).first()
        except Exception:
            return None
        finally:
            db.close()

    def create_oauth_user(self, oauth_data: Dict[str, Any]) -> tuple[Optional[User], Optional[str]]:
        db = self.get_db()
        try:
            existing_user = None
            if oauth_data.get("email"):
                existing_user = db.query(User).filter(User.email == oauth_data["email"]).first()

            if existing_user:
                if not existing_user.oauth_provider:
                    update_data = {
                        "oauth_provider": oauth_data.get("provider"),
                        "oauth_provider_id": oauth_data.get("provider_id"),
                        "oauth_data": json.dumps(oauth_data) if oauth_data else None,
                        "is_email_verified": True,
                        "status": "active",
                        "profile_picture": oauth_data.get("picture"),
                        "full_name": oauth_data.get("name")
                    }
                    
                    for key, value in update_data.items():
                        if hasattr(existing_user, key) and value is not None:
                            setattr(existing_user, key, value)
                    
                    db.commit()
                    db.refresh(existing_user)
                    return existing_user, None
                else:
                    return existing_user, None

            user_data = {
                "email": oauth_data.get("email"),
                "oauth_provider": oauth_data.get("provider"),
                "oauth_provider_id": oauth_data.get("provider_id"),
                "oauth_data": json.dumps(oauth_data) if oauth_data else None,
                "is_email_verified": True,
                "status": "active",
                "profile_picture": oauth_data.get("picture"),
                "full_name": oauth_data.get("name")
            }

            user = User(**user_data)
            db.add(user)
            db.commit()
            db.refresh(user)
            return user, None

        except IntegrityError as e:
            db.rollback()
            if "email" in str(e):
                return None, "Email already exists"
            else:
                return None, "User data conflict"
        except Exception as e:
            db.rollback()
            return None, f"Database error: {str(e)}"
        finally:
            db.close()

    def find_user_by_email_or_oauth(self, email: str = None, provider: str = None, provider_id: str = None) -> Optional[User]:
        db = self.get_db()
        try:
            query = db.query(User)
            
            conditions = []
            if email:
                conditions.append(User.email == email)
            if provider and provider_id:
                conditions.append(
                    (User.oauth_provider == provider) & 
                    (User.oauth_provider_id == provider_id)
                )
            
            if conditions:
                return query.filter(or_(*conditions)).first()
            return None
        except Exception:
            return None
        finally:
            db.close()


user_repository = UserRepository()