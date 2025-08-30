from datetime import datetime, timedelta, timezone
from typing import Optional, Union
from passlib.context import CryptContext
from jose import JWTError, jwt
import os
import secrets
import string
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from config.config_loader import config_loader
from services.repositories import get_user_repository # Add this import

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class AuthService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = os.getenv("SECRET_KEY")
        if not self.secret_key:
            raise ValueError("SECRET_KEY environment variable must be set")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            # Set default expiration to 30 minutes if not provided
            expire = datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None

    def generate_verification_token(self, length: int = 32) -> str:
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def validate_password_strength(self, password: str) -> tuple[bool, str]:
        if len(password) < 8:
            return False, config_loader.get_message("validation", "password_too_short")
        
        if not any(c.isupper() for c in password):
            return False, config_loader.get_message("validation", "password_no_uppercase")
        
        if not any(c.islower() for c in password):
            return False, config_loader.get_message("validation", "password_no_lowercase")
        
        if not any(c.isdigit() for c in password):
            return False, config_loader.get_message("validation", "password_no_number")
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            return False, config_loader.get_message("validation", "password_no_special")
        
        return True, config_loader.get_message("validation", "password_strong")
    

# get_current_user function moved to services/dependencies.py to avoid duplication

# Lazy loading to avoid environment variable issues during import
_auth_service_instance = None

def get_auth_service():
    global _auth_service_instance
    if _auth_service_instance is None:
        _auth_service_instance = AuthService()
    return _auth_service_instance