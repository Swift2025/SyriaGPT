from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
import re

from services.auth import auth_service
from services.user_repository import user_repository


class UserRegistrationRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    phone_number: Optional[str] = Field(None, regex=r'^\+?[1-9]\d{1,14}$')
    
    @validator('password')
    def validate_password(cls, v):
        is_valid, message = auth_service.validate_password_strength(v)
        if not is_valid:
            raise ValueError(message)
        return v
    
    @validator('phone_number')
    def validate_phone(cls, v):
        if v and not re.match(r'^\+?[1-9]\d{1,14}$', v):
            raise ValueError("Invalid phone number format")
        return v


class UserRegistrationResponse(BaseModel):
    id: str
    email: str
    phone_number: Optional[str]
    status: str
    is_email_verified: bool
    is_phone_verified: bool
    created_at: datetime
    message: str


class RegistrationService:
    def __init__(self):
        self.auth_service = auth_service
        self.user_repository = user_repository

    def register_user(self, registration_data: UserRegistrationRequest) -> tuple[Optional[UserRegistrationResponse], Optional[str], int]:
        try:
            existing_user = self.user_repository.get_user_by_email(registration_data.email)
            if existing_user:
                return None, "Email already registered", status.HTTP_409_CONFLICT

            if registration_data.phone_number:
                existing_phone = self.user_repository.get_user_by_phone(registration_data.phone_number)
                if existing_phone:
                    return None, "Phone number already registered", status.HTTP_409_CONFLICT

            hashed_password = self.auth_service.hash_password(registration_data.password)
            verification_token = self.auth_service.generate_verification_token()
            
            user_data = {
                "email": registration_data.email,
                "password_hash": hashed_password,
                "phone_number": registration_data.phone_number,
                "token": verification_token,
                "token_expiry": datetime.utcnow() + timedelta(hours=24),
                "status": "pending_verification",
                "is_email_verified": False,
                "is_phone_verified": False,
                "two_factor_enabled": False
            }

            user, error = self.user_repository.create_user(user_data)
            if error:
                return None, error, status.HTTP_400_BAD_REQUEST

            response = UserRegistrationResponse(
                id=str(user.id),
                email=user.email,
                phone_number=user.phone_number,
                status=user.status,
                is_email_verified=user.is_email_verified,
                is_phone_verified=user.is_phone_verified,
                created_at=user.created_at,
                message="Registration successful. Please verify your email address."
            )

            return response, None, status.HTTP_201_CREATED

        except ValueError as ve:
            return None, str(ve), status.HTTP_400_BAD_REQUEST
        except Exception as e:
            return None, f"Registration failed: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR

    def verify_email(self, token: str) -> tuple[bool, str, int]:
        try:
            from models.user import User
            db = self.user_repository.get_db()
            user = db.query(User).filter(
                User.token == token,
                User.token_expiry > datetime.utcnow()
            ).first()
            
            if not user:
                return False, "Invalid or expired verification token", status.HTTP_400_BAD_REQUEST

            update_data = {
                "is_email_verified": True,
                "status": "active",
                "token": None,
                "token_expiry": None
            }

            updated_user, error = self.user_repository.update_user(str(user.id), update_data)
            if error:
                return False, error, status.HTTP_500_INTERNAL_SERVER_ERROR

            return True, "Email verified successfully", status.HTTP_200_OK

        except Exception as e:
            return False, f"Verification failed: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR


registration_service = RegistrationService()
router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserRegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register_user(registration_data: UserRegistrationRequest):
    result, error, status_code = registration_service.register_user(registration_data)
    
    if error:
        raise HTTPException(status_code=status_code, detail=error)
    
    return result


@router.get("/verify-email/{token}")
async def verify_email(token: str):
    success, message, status_code = registration_service.verify_email(token)
    
    if not success:
        raise HTTPException(status_code=status_code, detail=message)
    
    return JSONResponse(
        status_code=status_code,
        content={"message": message, "verified": True}
    )


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "registration"}