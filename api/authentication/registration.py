from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Query, Request
from fastapi.responses import JSONResponse
import secrets
import uuid

from models.schemas.request_models import (
    UserRegistrationRequest,
    OAuthAuthorizationRequest,
    OAuthCallbackRequest
)
from models.schemas.response_models import (
    UserRegistrationResponse,
    EmailVerificationResponse,
    OAuthProvidersResponse,
    OAuthAuthorizationResponse,
    HealthResponse,
    ErrorResponse
)
from services.auth import get_auth_service
from services.repositories import get_user_repository
from services.email import get_email_service
from services.auth import get_oauth_service
from config.config_loader import config_loader


class RegistrationService:
    def __init__(self):
        self.user_repository = get_user_repository()
        self.config_loader = config_loader
    
    @property
    def email_service(self):
        return get_email_service()
    
    @property
    def oauth_service(self):
        return get_oauth_service()
    
    @property
    def auth_service(self):
        return get_auth_service()

    async def register_user(self, registration_data: UserRegistrationRequest) -> tuple[Optional[UserRegistrationResponse], Optional[str], int]:
        try:
            existing_user = self.user_repository.get_user_by_email(registration_data.email)
            if existing_user:
                return None, self.config_loader.get_message("errors", "email_exists"), status.HTTP_409_CONFLICT

            if registration_data.phone_number:
                existing_phone = self.user_repository.get_user_by_phone(registration_data.phone_number)
                if existing_phone:
                    return None, self.config_loader.get_message("errors", "phone_exists"), status.HTTP_409_CONFLICT

            hashed_password = self.auth_service.hash_password(registration_data.password)
            verification_token = self.auth_service.generate_verification_token()
            registration_token = self.auth_service.create_access_token({"sub": registration_data.email})
            
            full_name = self._build_full_name(registration_data.first_name, registration_data.last_name)
            
            user_data = {
                "email": registration_data.email,
                "password_hash": hashed_password,
                "phone_number": registration_data.phone_number,
                "first_name": registration_data.first_name,
                "last_name": registration_data.last_name,
                "full_name": full_name,
                "token": verification_token,
                "token_expiry": datetime.now(timezone.utc) + timedelta(hours=24),
                "status": "pending_verification",
                "is_email_verified": False,
                "is_phone_verified": False,
                "two_factor_enabled": False
            }

            user, error = self.user_repository.create_user(user_data)
            if error:
                return None, error, status.HTTP_400_BAD_REQUEST

            message = self.config_loader.get_message("registration", "success")
            if self.email_service.is_configured():
                email_sent, email_error = await self.email_service.send_verification_email(
                    to_email=user.email,
                    verification_token=verification_token,
                    user_name=user.full_name
                )
                if email_sent:
                    message = self.config_loader.get_message("registration", "email_verification_sent")
                else:
                    message = self.config_loader.get_message("registration", "email_send_failed")

            response = UserRegistrationResponse(
                id=str(user.id),
                email=user.email,
                phone_number=user.phone_number,
                full_name=user.full_name,
                profile_picture=user.profile_picture,
                oauth_provider=user.oauth_provider,
                status=user.status,
                is_email_verified=user.is_email_verified,
                is_phone_verified=user.is_phone_verified,
                created_at=user.created_at,
                registration_token=registration_token,
                message=message
            )

            return response, None, status.HTTP_201_CREATED

        except ValueError as ve:
            return None, str(ve), status.HTTP_400_BAD_REQUEST
        except Exception as e:
            return None, self.config_loader.get_message("errors", "registration_failed", error=str(e)), status.HTTP_500_INTERNAL_SERVER_ERROR

    async def verify_email(self, token: str) -> tuple[bool, EmailVerificationResponse, int]:
        try:
            from models.domain.user import User
            db = self.user_repository.get_db()
            user = db.query(User).filter(
                User.token == token,
                User.token_expiry > datetime.now(timezone.utc)
            ).first()
            
            if not user:
                return False, None, status.HTTP_400_BAD_REQUEST

            update_data = {
                "is_email_verified": True,
                "status": "active",
                "token": None,
                "token_expiry": None
            }

            updated_user, error = self.user_repository.update_user(str(user.id), update_data)
            if error:
                return False, None, status.HTTP_500_INTERNAL_SERVER_ERROR

            if self.email_service.is_configured():
                await self.email_service.send_welcome_email(
                    to_email=user.email,
                    user_name=updated_user.full_name
                )

            response = EmailVerificationResponse(
                message=self.config_loader.get_message("verification", "success"),
                verified=True,
                user_id=str(updated_user.id),
                email=updated_user.email
            )

            return True, response, status.HTTP_200_OK

        except Exception as e:
            return False, None, status.HTTP_500_INTERNAL_SERVER_ERROR

    async def oauth_register(self, provider: str, oauth_data: Dict[str, Any]) -> tuple[Optional[UserRegistrationResponse], Optional[str], int]:
        try:
            if not oauth_data or not oauth_data.get("email"):
                return None, self.config_loader.get_message("errors", "oauth_no_email"), status.HTTP_400_BAD_REQUEST

            user, error = self.user_repository.create_oauth_user(oauth_data)
            if error:
                return None, error, status.HTTP_400_BAD_REQUEST

            registration_token = self.auth_service.create_access_token({"sub": user.email})

            response = UserRegistrationResponse(
                id=str(user.id),
                email=user.email,
                phone_number=user.phone_number,
                full_name=user.full_name,
                profile_picture=user.profile_picture,
                oauth_provider=user.oauth_provider,
                status=user.status,
                is_email_verified=user.is_email_verified,
                is_phone_verified=user.is_phone_verified,
                created_at=user.created_at,
                registration_token=registration_token,
                message=self.config_loader.get_message("registration", "success_oauth", provider=provider.title())
            )

            return response, None, status.HTTP_201_CREATED

        except Exception as e:
            return None, self.config_loader.get_message("errors", "oauth_failed", error=str(e)), status.HTTP_500_INTERNAL_SERVER_ERROR

    def get_oauth_authorization_url(self, provider: str, redirect_uri: str) -> tuple[Optional[OAuthAuthorizationResponse], Optional[str], int]:
        try:
            if not self.oauth_service.is_configured(provider):
                return None, self.config_loader.get_message("errors", "oauth_not_configured", provider=provider), status.HTTP_400_BAD_REQUEST

            state = secrets.token_urlsafe(32)
            authorization_url = self.oauth_service.get_authorization_url(provider, redirect_uri, state)
            
            response = OAuthAuthorizationResponse(
                authorization_url=authorization_url,
                redirect_uri=redirect_uri,
                state=state,
                provider=provider
            )
            
            return response, None, status.HTTP_200_OK

        except Exception as e:
            return None, self.config_loader.get_message("errors", "authorization_url_failed", error=str(e)), status.HTTP_500_INTERNAL_SERVER_ERROR

    async def oauth_callback(self, provider: str, code: str, redirect_uri: str) -> tuple[Optional[UserRegistrationResponse], Optional[str], int]:
        try:
            if not self.oauth_service.is_configured(provider):
                return None, self.config_loader.get_message("errors", "oauth_not_configured", provider=provider), status.HTTP_400_BAD_REQUEST

            oauth_data = await self.oauth_service.get_user_info(provider, code, redirect_uri)
            if not oauth_data:
                return None, self.config_loader.get_message("errors", "oauth_user_info_failed"), status.HTTP_400_BAD_REQUEST

            return await self.oauth_register(provider, oauth_data)

        except Exception as e:
            return None, self.config_loader.get_message("errors", "oauth_callback_failed", error=str(e)), status.HTTP_500_INTERNAL_SERVER_ERROR

    def get_health_status(self) -> HealthResponse:
        return HealthResponse(
            status=self.config_loader.get_message("service", "healthy"),
            service=self.config_loader.get_message("service", "registration_service"),
            email_configured=self.email_service.is_configured(),
            oauth_providers=self.oauth_service.get_available_providers(),
            database_connected=self._check_database_connection(),
            version=self.config_loader.get_message("service", "version")
        )

    def get_oauth_providers_info(self) -> OAuthProvidersResponse:
        available_providers = self.oauth_service.get_available_providers()
        configured_providers = {
            provider: self.oauth_service.is_configured(provider)
            for provider in ["google", "facebook"]
        }
        
        return OAuthProvidersResponse(
            providers=available_providers,
            configured_providers=configured_providers
        )

    def _build_full_name(self, first_name: Optional[str], last_name: Optional[str]) -> Optional[str]:
        if not first_name and not last_name:
            return None
        
        name_parts = []
        if first_name:
            name_parts.append(first_name.strip())
        if last_name:
            name_parts.append(last_name.strip())
        
        return " ".join(name_parts) if name_parts else None

    def _check_database_connection(self) -> bool:
        try:
            db = self.user_repository.get_db()
            db.execute("SELECT 1")
            db.close()
            return True
        except Exception:
            return False