# /api/authentication/routes.py

from fastapi import APIRouter, Request, HTTPException, status, Query, Depends
from typing import Optional

from models.domain.user import User
from models.schemas.request_models import UserLoginRequest, SocialLoginRequest, UserRegistrationRequest, ForgotPasswordRequest, ResetPasswordRequest, TwoFactorVerifyRequest
from models.schemas.response_models import LoginResponse, ErrorResponse, UserRegistrationResponse, EmailVerificationResponse, OAuthProvidersResponse, OAuthAuthorizationResponse, HealthResponse, TwoFactorSetupResponse, GeneralResponse
from .authentication import AuthenticationService
from .registration import RegistrationService
from .two_factor import TwoFactorService
from services.auth import get_forgot_password_service
from services.dependencies import get_current_user
from config.config_loader import config_loader

authentication_service = AuthenticationService()
registration_service = RegistrationService()
two_factor_service = TwoFactorService()

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/login",
    response_model=LoginResponse,
    responses={401: {"model": ErrorResponse}}
)
async def login_user(login_data: UserLoginRequest):
    return await authentication_service.login_user(login_data)


# Removed separate social login endpoint - now merged with OAuth callback


@router.post("/register", response_model=UserRegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register_user(registration_data: UserRegistrationRequest):
    result, error, status_code = await registration_service.register_user(registration_data)
    
    if error:
        raise HTTPException(status_code=status_code, detail=error)
    
    return result


@router.get("/verify-email/{token}", response_model=EmailVerificationResponse)
async def verify_email(token: str):
    success, response, status_code = await registration_service.verify_email(token)
    
    if not success:
        error_msg = config_loader.get_message("verification", "invalid_token")
        raise HTTPException(status_code=status_code, detail=error_msg)
    
    return response


@router.get("/oauth/providers", response_model=OAuthProvidersResponse)
async def get_oauth_providers():
    return registration_service.get_oauth_providers_info()


@router.post("/oauth/{provider}/authorize", response_model=OAuthAuthorizationResponse)
async def oauth_authorize(
    provider: str,
    request: Request,
    redirect_uri: Optional[str] = Query(None)
):
    if redirect_uri is None:
        redirect_uri = f"{request.base_url}auth/oauth/{provider}/callback"
    
    response, error, status_code = registration_service.get_oauth_authorization_url(provider, redirect_uri)
    
    if error:
        raise HTTPException(status_code=status_code, detail=error)
    
    return response


@router.get("/oauth/{provider}/callback", response_model=LoginResponse)
async def oauth_callback(
    provider: str,
    code: str = Query(...),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    request: Request = None
):
    """
    OAuth callback endpoint - handles both user registration and login.
    If user exists, logs them in. If user doesn't exist, registers and logs them in.
    """
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth error: {error}"
        )
    
    redirect_uri = f"{request.base_url}auth/oauth/{provider}/callback"
    
    # Use social_login method which handles both registration and login
    from models.schemas.request_models import SocialLoginRequest
    social_request = SocialLoginRequest(
        provider=provider,
        code=code,
        redirect_uri=redirect_uri
    )
    
    return await authentication_service.social_login(social_request, request)


@router.post("/oauth/{provider}/login", response_model=LoginResponse)
async def oauth_login(
    provider: str,
    request: Request,
    code: str = Query(...),
    redirect_uri: Optional[str] = Query(None)
):
    """
    POST endpoint for OAuth login - alternative to GET callback.
    Handles both user registration and login via OAuth.
    """
    if redirect_uri is None:
        redirect_uri = f"{request.base_url}auth/oauth/{provider}/callback"
    
    # Use social_login method which handles both registration and login
    from models.schemas.request_models import SocialLoginRequest
    social_request = SocialLoginRequest(
        provider=provider,
        code=code,
        redirect_uri=redirect_uri
    )
    
    return await authentication_service.social_login(social_request, request)


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return registration_service.get_health_status()

@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest):
    forgot_password_service = get_forgot_password_service()
    token = forgot_password_service.create_reset_token(request.email)
    forgot_password_service.send_reset_email(request.email, token)
    return {"msg": "تم إرسال رابط إعادة التعيين إلى بريدك الإلكتروني"}

# Endpoint: إعادة التعيين
@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest):
    forgot_password_service = get_forgot_password_service()
    forgot_password_service.reset_password(request.token, request.new_password, request.confirm_password)
    return {"msg": "تمت إعادة تعيين كلمة المرور بنجاح، وتم تسجيل خروجك من جميع الأجهزة"}

@router.post("/2fa/setup", response_model=TwoFactorSetupResponse)

def setup_2fa_endpoint(current_user: User = Depends(get_current_user)):
    return two_factor_service.setup_2fa(current_user)

@router.post("/2fa/verify", response_model=GeneralResponse)

def verify_2fa_endpoint(verify_data: TwoFactorVerifyRequest, current_user: User = Depends(get_current_user)):
    return two_factor_service.verify_and_enable_2fa(current_user, verify_data)

@router.post("/2fa/disable", response_model=GeneralResponse)
def disable_2fa_endpoint(current_user: User = Depends(get_current_user)):
    return two_factor_service.disable_2fa(current_user)


# TEST ENDPOINT - FOR DEMO PURPOSES ONLY
@router.post("/test/generate-token")
def generate_test_token():
    """
    🧪 TEST ENDPOINT - Generate a test token for Swagger UI authentication
    
    **FOR DEVELOPMENT/TESTING ONLY**
    
    Returns a valid JWT token that can be used to authenticate in Swagger UI.
    Copy the access_token and use it in the Authorize button.
    """
    import os
    
    # Only allow in development environment
    if os.getenv("ENV") != "development":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Test endpoint only available in development environment"
        )
    
    from services.auth import get_auth_service
    from datetime import timedelta
    
    # Create a test token with fake user data
    auth_service = get_auth_service()
    test_token = auth_service.create_access_token(
        data={"sub": "test@example.com", "session_id": "test-session"},
        expires_delta=timedelta(hours=1)
    )
    
    return {
        "access_token": test_token,
        "token_type": "bearer",
        "expires_in": 3600,
        "usage": "Copy the access_token above, click 'Authorize' in Swagger UI, and paste: Bearer YOUR_ACCESS_TOKEN"
    }
