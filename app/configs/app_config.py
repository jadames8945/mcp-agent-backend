import os
from typing import cast, Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class AppConfig(BaseSettings):
    ENV: str = cast(str, os.getenv("ENV", "DEV"))
    PORT: int = int(os.getenv("PORT", "8945"))
    DEBUGGER: Optional[str] = cast(Optional[str], os.getenv("DEBUGGER", None))
    DEBUGGER_PORT: int = int(os.getenv("DEBUGGER_PORT", "5678"))

    def allowed_origins(self):
        env_origins = os.getenv("ALLOWED_ORIGINS")
        if env_origins:
            return [origin.strip() for origin in env_origins.split(",")]

        return [
            "https://mcp-nav.coolify.dd-dpe.com",
            "http://localhost:3000",
            "https://mcp-be.coolify.dd-dpe.com",
            "http://mcp-nav.coolify.dd-dpe.com",
            "http://mcp-be.coolify.dd-dpe.com",
            "*"
        ]


config = AppConfig()
