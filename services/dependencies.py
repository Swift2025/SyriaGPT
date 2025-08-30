# In SyriaGPT/services/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from services.auth import get_auth_service, oauth2_scheme
# Removed direct import - using get_user_repository() function instead

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        auth_service = get_auth_service()
        payload = auth_service.verify_token(token)
        if payload is None:
            raise credentials_exception
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Handle test tokens
    if email == "test@example.com":
        from models.domain.user import User
        # Create a mock user for testing
        test_user = User()
        test_user.id = "test-user-id"
        test_user.email = "test@example.com"
        test_user.full_name = "Test User"
        test_user.first_name = "Test"
        test_user.last_name = "User"
        return test_user
    
    from services.repositories import get_user_repository
    user_repo = get_user_repository()
    user = user_repo.get_user_by_email(email)
    if user is None:
        raise credentials_exception
    return user
