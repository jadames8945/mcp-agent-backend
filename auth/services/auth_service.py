import logging
from typing import Optional

from auth.repositories.auth_repository import AuthRepository
from auth.schemas.token import Token
from auth.schemas.user import UserCredentials, User
from auth.services.token_service import TokenService

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self):
        self.token_service = TokenService()
        self.auth_repository = AuthRepository()

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = self.auth_repository.get_user_by_username(username)

        if not user:
            return None

        if not self.token_service.verify_password(password, user.password):
            return None

        return user

    def register_user(
            self,
            user: User
    ) -> User:
        logger.info(f"Attempting to register user: {user.username}")

        try:
            existing_user = self.auth_repository.get_user_by_username(user.username)

            if existing_user:
                raise ValueError("Username already exists")

            user.password = self.token_service.get_password_hash(user.password)

            logger.info("Password hashed successfully")

            created_user: User = self.auth_repository.create_user(user)

            logger.info(f"User created in database: {created_user.username}")

            return created_user

        except Exception as e:
            logger.error(f"Error in register_user: {e}")
            raise

    def login_user(self, credentials: UserCredentials) -> Token:
        try:
            user = self.authenticate_user(credentials.username, credentials.password)

            if not user:
                raise ValueError("Invalid username or password")

            logger.info(f"Creating token for user: {user.username}")

            access_token = self.token_service.create_access_token(data={"username": user.username})

            logger.info("Token created successfully")

            return Token(access_token=access_token, user=user.model_dump())
        except Exception as e:
            logger.error(f"Error in login_user: {e}")
            raise
