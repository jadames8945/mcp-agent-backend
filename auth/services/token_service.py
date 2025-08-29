from datetime import datetime, timedelta
from typing import Optional

import jwt
import pytz
from passlib.context import CryptContext

from auth.configs.auth_settings import AuthSettings


class TokenService:
    def __init__(self):
        self.ACCESS_TOKEN_EXPIRE_MINUTES = AuthSettings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.SECRET_KEY = AuthSettings.SECRET_KEY
        self.ALGORITHM = AuthSettings.ALGORITHM
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def create_access_token(self, data: dict):
        to_encode = data.copy()

        eastern_timezone = pytz.timezone('US/Eastern')

        current_eastern_time = datetime.now(eastern_timezone)

        expire = current_eastern_time + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"token_expires": expire.isoformat()})

        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

        return encoded_jwt

    def verify_token(self, token: str) -> Optional[str]:
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            username: str = payload.get("username")
            if username is None:
                return None
            return username
        except jwt.PyJWTError:
            return None

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)
