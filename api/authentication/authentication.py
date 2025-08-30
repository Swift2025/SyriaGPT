# /api/authentication/authentication.py

from fastapi import HTTPException, status, Request
from datetime import datetime, timezone, timedelta

from models.schemas.request_models import SocialLoginRequest, UserLoginRequest
from models.schemas.response_models import LoginResponse, ErrorResponse
from services.auth import get_oauth_service
from services.repositories import get_user_repository
from services.auth import get_auth_service
from config.config_loader import config_loader
from services.auth import get_two_factor_auth_service

class AuthenticationService:
    def __init__(self):
        self.user_repository = get_user_repository()
        self.config_loader = config_loader
    
    @property
    def oauth_service(self):
        return get_oauth_service()
    
    @property
    def auth_service(self):
        return get_auth_service()

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
        self.user_repository.update_user(str(user.id), {"last_login_at": datetime.now(timezone.utc)})

        # 5. إنشاء Access Token
        access_token = self.auth_service.create_access_token(data={"sub": user.email})

        return LoginResponse(
            access_token=access_token,
            user_id=str(user.id),
            email=user.email,
            full_name=user.full_name
        )
    
    async def login_user(self, login_data: UserLoginRequest):
        # 1. البحث عن المستخدم والتحقق من كلمة المرور (نفس الكود السابق)
        user = self.user_repository.get_user_by_email(login_data.email)
        if not user or not user.password_hash:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=self.config_loader.get_message("errors", "invalid_credentials")
            )
        is_password_valid = self.auth_service.verify_password(login_data.password, user.password_hash)
        if not is_password_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=self.config_loader.get_message("errors", "invalid_credentials")
            )

        # 2. التحقق من المصادقة الثنائية
        if user.two_factor_enabled:
            if not login_data.two_factor_code:
                # إذا كانت 2FA مفعلة ولم يتم إرسال الرمز، اطلب من المستخدم إدخاله
                return LoginResponse(
                    user_id=str(user.id),
                    email=user.email,
                    full_name=user.full_name,
                    two_factor_required=True,
                    message="Please provide your 2FA code."
                )
            
            # تحقق من صحة الرمز
            two_factor_service = get_two_factor_auth_service()
            is_code_valid = two_factor_service.verify_code(
                user.two_factor_secret, login_data.two_factor_code
            )
            if not is_code_valid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid 2FA code."
                )

        # 3. تحديث تاريخ آخر تسجيل دخول وإنشاء Token (نفس الكود السابق)
        self.user_repository.update_user(str(user.id), {"last_login_at": datetime.now(timezone.utc)})
        if login_data.remember_me:
            expires_delta = timedelta(days=30)
        else:
            expires_delta = timedelta(minutes=self.auth_service.access_token_expire_minutes)
        access_token = self.auth_service.create_access_token(
            data={"sub": user.email}, expires_delta=expires_delta
        )

        return LoginResponse(
            access_token=access_token,
            user_id=str(user.id),
            email=user.email,
            full_name=user.full_name
        )


