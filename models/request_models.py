from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
import re



from services.auth import auth_service


class UserRegistrationRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    phone_number: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    
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