from datetime import datetime, timedelta, timezone
import smtplib
from passlib.context import CryptContext
from jose import JWTError, jwt
import os
from email.mime.text import MIMEText
from sqlalchemy.orm import Session
from models.user import User
from services.auth import AuthService
from services.database import SessionLocal
from fastapi import HTTPException



class ForgotPasswordService:
    def __init__(self, db: Session):
        self.db = db
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
        self.algorithm = "HS256"
        self.reset_token_expire_minutes = 60
        self.smtp_server =  os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_user = os.getenv("SMTP_USER", "looka1584@gmail.com")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "jymhzkthkmsgltdz")
        
        
    def create_reset_token(self, email: str) -> str:
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise ValueError("المستخدم غير موجود")

        expire = datetime.utcnow() + timedelta(minutes=self.reset_token_expire_minutes)
        payload = {"sub": email, "exp": expire}
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

        user.reset_token = token
        user.reset_token_expiry = expire
        self.db.commit()

        return token
    
    
    def send_reset_email(self, email: str, token: str):
        reset_link = f"http://localhost:8000/reset-password?token={token}"
        msg = MIMEText(f"اضغط على الرابط لإعادة تعيين كلمة المرور:\n{reset_link}")
        msg["Subject"] = "إعادة تعيين كلمة المرور"
        msg["From"] = self.smtp_user
        msg["To"] = email

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)
    
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

        valid, msg = AuthService().validate_password_strength(new_password)
        if not valid:
            raise HTTPException(status_code=400, detail=msg)

        user.password_hash = self.hash_password(new_password)
        user.reset_token = None
        user.reset_token_expiry = None
        user.token = None
        user.last_password_change = datetime.utcnow()
        self.db.commit()
        return True
    
    def hash_password(self, password: str) -> str:
        """تشفير كلمة المرور"""
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """التحقق من كلمة المرور"""
        return self.pwd_context.verify(plain_password, hashed_password)

forgot_password_service = ForgotPasswordService(SessionLocal())