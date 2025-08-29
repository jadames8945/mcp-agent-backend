from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth.services.auth_service import AuthService
from auth.schemas.token import TokenData

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), auth_service: AuthService = Depends(AuthService)):
    """
    Dependency to get the current authenticated user from JWT token.
    Use this to protect endpoints that require authentication.
    """
    token = credentials.credentials
    username = auth_service.verify_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenData(username=username)

def get_current_username(current_user: TokenData = Depends(get_current_user)) -> str:
    """
    Dependency to get just the username from the authenticated user.
    """
    return current_user.username 