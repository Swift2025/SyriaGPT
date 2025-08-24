# /requests/authentication/authentication.py

from fastapi import APIRouter, HTTPException, status, Request
from datetime import datetime

from models.request_models import SocialLoginRequest
from models.response_models import LoginResponse, ErrorResponse
from services.oauth_service import oauth_service
from services.user_repository import user_repository
from services.auth import auth_service
from config.config_loader import config_loader

router = APIRouter(prefix="/auth", tags=["authentication"])

class AuthenticationService:
    def __init__(self):
        self.oauth_service = oauth_service
        self.user_repository = user_repository
        self.auth_service = auth_service
        self.config_loader = config_loader

    async def social_login(self, request_data: SocialLoginRequest, request: Request):
        redirect_uri = request_data.redirect_uri or f"{request.base_url}auth/oauth/{request_data.provider}/callback"
        
        # 1. الحصول على معلومات المستخدم من جوجل
        user_info = await self.oauth_service.get_user_info(
            request_data.provider, request_data.code, redirect_uri
        )
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=self.config_loader.get_message("errors", "oauth_user_info_failed")
            )
            
        # 2. البحث عن المستخدم في قاعدة البيانات
        provider_id = user_info.get("provider_id")
        user = self.user_repository.find_user_by_oauth(request_data.provider, provider_id)

        # 3. إذا لم يكن المستخدم موجوداً، قم بإنشاء حساب جديد
        if not user:
            user, error = self.user_repository.create_oauth_user(user_info)
            if error:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error)
        
        # 4. تحديث تاريخ آخر تسجيل دخول
        self.user_repository.update_user(str(user.id), {"last_login_at": datetime.utcnow()})

        # 5. إنشاء Access Token
        access_token = self.auth_service.create_access_token(data={"sub": user.email})

        return LoginResponse(
            access_token=access_token,
            user_id=str(user.id),
            email=user.email,
            full_name=user.full_name
        )

authentication_service = AuthenticationService()

@router.post(
    "/login/social",
    response_model=LoginResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def login_social(request_data: SocialLoginRequest, request: Request):
    return await authentication_service.social_login(request_data, request)