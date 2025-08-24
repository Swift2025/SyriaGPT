from pydantic import BaseModel, EmailStr
from fastapi import APIRouter

from services.forgot_password_service import forgot_password_service

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    confirm_password: str
    
router = APIRouter(prefix="/auth", tags=["forgotpassword"])    

@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest):
    token = forgot_password_service.create_reset_token(request.email)
    forgot_password_service.send_reset_email(request.email, token)
    return {"msg": "تم إرسال رابط إعادة التعيين إلى بريدك الإلكتروني"}

# Endpoint: إعادة التعيين
@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest):
    forgot_password_service.reset_password(request.token, request.new_password, request.confirm_password)
    return {"msg": "تمت إعادة تعيين كلمة المرور بنجاح، وتم تسجيل خروجك من جميع الأجهزة"}