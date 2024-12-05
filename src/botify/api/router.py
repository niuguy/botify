from fastapi import APIRouter
from .v1 import chat

router = APIRouter(prefix="/api/v1")

router.include_router(chat.router)  
