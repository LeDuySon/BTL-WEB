from fastapi import APIRouter

from .endpoints.user import router as user_router
from .endpoints.authentication import router as auth_router
from .endpoints.home import router as home_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(user_router)
router.include_router(home_router)
