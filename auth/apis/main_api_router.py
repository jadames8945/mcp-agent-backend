from fastapi import APIRouter
from auth.apis.auth.router import auth_router

api_router = APIRouter()
api_router.include_router(auth_router)
