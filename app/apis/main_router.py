from fastapi import APIRouter

from app.apis.tool_summary.router import router as tool_summary_router

main_router = APIRouter()

main_router.include_router(tool_summary_router)

# Add auth routes
from auth.apis.auth.router import auth_router
main_router.include_router(auth_router)

# Add config routes
from app.apis.configs.router import router as configs_router
main_router.include_router(configs_router)

# Add chat routes
from app.apis.chat.router import router as chat_router
main_router.include_router(chat_router)
