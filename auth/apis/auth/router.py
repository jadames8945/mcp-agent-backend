from fastapi import APIRouter, Depends, HTTPException

from auth.exceptions.user_exceptions import check_credentials, MissingCredentialsException, UserException
from auth.schemas.token import Token
from auth.schemas.user import UserCredentials, User
from auth.services.auth_service import AuthService

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


def get_auth_service():
    return AuthService()


@auth_router.post("/register", response_model=User)
def register_user(
        user: User,
        auth_service: AuthService = Depends(get_auth_service)
) -> User:
    try:
        check_credentials(user.username, user.password)

        user_response = auth_service.register_user(user)

        return user_response
    except MissingCredentialsException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UserException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@auth_router.post("/login", response_model=Token)
def login_user(
        user_credentials: UserCredentials,
        auth_service: AuthService = Depends(get_auth_service)
) -> Token:
    try:
        check_credentials(user_credentials.username, user_credentials.password)
        token = auth_service.login_user(user_credentials)
        return token
    except MissingCredentialsException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except UserException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
