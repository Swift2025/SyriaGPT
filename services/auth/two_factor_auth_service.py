# In SyriaGPT/services/two_factor_auth_service.py

import pyotp
import qrcode
import io
import base64

class TwoFactorAuthService:
    def generate_secret(self) -> str:
        """
        Generates a new base32 secret key for 2FA.
        """
        return pyotp.random_base32()

    def verify_code(self, secret: str, code: str) -> bool:
        """
        Verifies the 2FA code provided by the user.
        """
        totp = pyotp.TOTP(secret)
        return totp.verify(code)

    def get_provisioning_uri(self, email: str, secret: str, issuer_name: str = "SyriaGPT") -> str:
        """
        Generates the provisioning URI for the authenticator app.
        """
        return pyotp.totp.TOTP(secret).provisioning_uri(
            name=email,
            issuer_name=issuer_name
        )

    def generate_qr_code(self, uri: str) -> str:
        """
        Generates a QR code image from the provisioning URI and returns it as a base64 encoded string.
        """
        img = qrcode.make(uri)
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{img_str}"

# Lazy loading to avoid import issues
_two_factor_auth_service_instance = None

def get_two_factor_auth_service():
    global _two_factor_auth_service_instance
    if _two_factor_auth_service_instance is None:
        _two_factor_auth_service_instance = TwoFactorAuthService()
    return _two_factor_auth_service_instance

two_factor_auth_service = get_two_factor_auth_service()