from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class UserRegistrationResponse(BaseModel):
    id: str
    email: str
    phone_number: Optional[str]
    full_name: Optional[str]
    profile_picture: Optional[str]
    oauth_provider: Optional[str]
    status: str
    is_email_verified: bool
    is_phone_verified: bool
    created_at: datetime
    registration_token: Optional[str]
    message: str


class EmailVerificationResponse(BaseModel):
    message: str
    verified: bool
    user_id: str
    email: str


class OAuthProvidersResponse(BaseModel):
    providers: list[str]
    configured_providers: Dict[str, bool]


class OAuthAuthorizationResponse(BaseModel):
    authorization_url: str
    redirect_uri: str
    state: str
    provider: str


class HealthResponse(BaseModel):
    status: str
    service: str
    email_configured: bool
    oauth_providers: list[str]
    database_connected: bool
    version: str


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    status_code: int


class LoginResponse(BaseModel):
    access_token: Optional[str] = None # <-- MAKE THIS OPTIONAL
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    full_name: Optional[str] = None
    two_factor_required: bool = False # <-- ADD THIS LINE
    message: Optional[str] = None     # <-- ADD THIS LINE    

class TwoFactorSetupResponse(BaseModel):
    secret_key: str
    qr_code: str # This will be a base64 encoded image string

class GeneralResponse(BaseModel):
    status: str
    message: str


class QuestionResponse(BaseModel):
    id: str
    user_id: str
    question: str
    created_at: datetime
    updated_at: datetime


class AnswerResponse(BaseModel):
    id: str
    answer: str
    question_id: str
    user_id: str
    created_at: datetime
    author: str


class QuestionWithAnswersResponse(BaseModel):
    question: QuestionResponse
    answers: list[AnswerResponse]    