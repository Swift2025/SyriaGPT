# In SyriaGPT/requests/authentication/two_factor_service.py

from fastapi import HTTPException
from models.user import User
from models.response_models import TwoFactorSetupResponse, GeneralResponse
from models.request_models import TwoFactorVerifyRequest
from services.user_repository import user_repository
from services.two_factor_auth_service import two_factor_auth_service

class TwoFactorService:
    def setup_2fa(self, current_user: User):
        # 1. Generate a new secret
        secret = two_factor_auth_service.generate_secret()

        # 2. Update user with the new secret (but don't enable it yet)
        user_repository.update_user(str(current_user.id), {"two_factor_secret": secret, "two_factor_enabled": False})

        # 3. Generate QR code
        uri = two_factor_auth_service.get_provisioning_uri(current_user.email, secret)
        qr_code = two_factor_auth_service.generate_qr_code(uri)

        return TwoFactorSetupResponse(secret_key=secret, qr_code=qr_code)

    def verify_and_enable_2fa(self, current_user: User, verify_data: TwoFactorVerifyRequest):
        if not current_user.two_factor_secret:
            raise HTTPException(status_code=400, detail="2FA is not set up. Please set it up first.")

        # 1. Verify the code
        is_valid = two_factor_auth_service.verify_code(current_user.two_factor_secret, verify_data.code)
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid 2FA code.")

        # 2. Enable 2FA for the user
        user_repository.update_user(str(current_user.id), {"two_factor_enabled": True})

        return GeneralResponse(status="success", message="2FA has been successfully enabled.")

    def disable_2fa(self, current_user: User):
        if not current_user.two_factor_enabled:
            raise HTTPException(status_code=400, detail="2FA is not currently enabled.")

        # Disable 2FA
        user_repository.update_user(str(current_user.id), {"two_factor_enabled": False, "two_factor_secret": None})
        
        return GeneralResponse(status="success", message="2FA has been disabled.")

two_factor_service = TwoFactorService()
