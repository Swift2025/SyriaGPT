from datetime import datetime, timedelta, timezone
import smtplib
from jose import JWTError, jwt
import os
from email.mime.text import MIMEText
from sqlalchemy.orm import Session
from models.domain.user import User
from services.auth import get_auth_service
from services.database import SessionLocal
from services.email import get_email_service
from fastapi import HTTPException



class ForgotPasswordService:
    def __init__(self, db: Session):
        self.db = db
        self.auth_service = get_auth_service()
        self.secret_key = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
        self.algorithm = "HS256"
        self.reset_token_expire_minutes = 60
        
        
    def create_reset_token(self, email: str) -> str:
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=400, detail="المستخدم غير موجود")

        expire = datetime.now(timezone.utc) + timedelta(minutes=self.reset_token_expire_minutes)
        payload = {"sub": email, "exp": expire}
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

        user.reset_token = token
        user.reset_token_expiry = expire
        self.db.commit()

        return token
    
    
    async def send_reset_email(self, email: str, token: str):
        """Send password reset email using the email service"""
        reset_link = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/reset-password?token={token}"
        
        # Use the email service instead of direct SMTP
        email_service = get_email_service()
        success, error = await email_service.send_password_reset_email(email, reset_link)
        if not success:
            raise HTTPException(status_code=500, detail=f"Failed to send reset email: {error}")
    
    def verify_reset_token(self, token: str):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email: str = payload.get("sub")
            if email is None:
                return None

            user = self.db.query(User).filter(User.email == email).first()
            if not user or user.reset_token != token:
                return None
            if user.reset_token_expiry < datetime.now(timezone.utc):
                return None
            return user
        except JWTError:
            return None
    
    def reset_password(self, token: str, new_password: str, confirm_password: str):
        user = self.verify_reset_token(token)
        if not user:
            raise HTTPException(status_code=400, detail="رمز إعادة التعيين غير صالح أو منتهي الصلاحية")

        if new_password != confirm_password:
            raise HTTPException(status_code=400, detail="كلمتا المرور غير متطابقتين")

        valid, msg = self.auth_service.validate_password_strength(new_password)
        if not valid:
            raise HTTPException(status_code=400, detail=msg)

        user.password_hash = self.auth_service.hash_password(new_password)
        user.reset_token = None
        user.reset_token_expiry = None
        user.token = None
        user.token_expiry = None
        user.last_password_change = datetime.now(timezone.utc)
        self.db.commit()
        return True
    
    # Password hashing methods removed - now using auth_service

# Lazy loading to avoid environment variable issues during import
_forgot_password_service_instance = None

def get_forgot_password_service():
    global _forgot_password_service_instance
    if _forgot_password_service_instance is None:
        _forgot_password_service_instance = ForgotPasswordService(SessionLocal())
    return _forgot_password_service_instance