from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
import re


class UserRegistrationRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    phone_number: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        # Basic password validation to avoid circular imports
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v):
            raise ValueError("Password must contain at least one special character")
        return v
    
    @validator('phone_number')
    def validate_phone(cls, v):
        if v and not re.match(r'^\+?[1-9]\d{1,14}$', v):
            raise ValueError("Invalid phone number format")
        return v


class OAuthAuthorizationRequest(BaseModel):
    provider: str = Field(..., pattern=r'^(google|facebook)$')
    redirect_uri: Optional[str] = None


class OAuthCallbackRequest(BaseModel):
    provider: str = Field(..., pattern=r'^(google|facebook)$')
    code: str
    state: Optional[str] = None
    redirect_uri: Optional[str] = None

class SocialLoginRequest(BaseModel):
    provider: str = Field(..., pattern=r'^(google|facebook)$')
    code: str
    redirect_uri: Optional[str] = None    




class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: Optional[bool] = False
    two_factor_code: Optional[str] = None


class TwoFactorVerifyRequest(BaseModel):
    code: str = Field(..., min_length=6, max_length=6)


class QuestionCreateRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=10000)


class AnswerCreateRequest(BaseModel):
    answer: str = Field(..., min_length=1, max_length=10000)
    question_id: str = Field(..., description="UUID of the question")
    author: str = Field(..., min_length=1, max_length=255)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)
    
    @validator('confirm_password')
    def validate_passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError("Passwords do not match")
        return v
    
    @validator('new_password')
    def validate_password_strength(cls, v):
        # Basic password validation to avoid circular imports
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v):
            raise ValueError("Password must contain at least one special character")
        return v    