from aiogram import Router
from .main import router as user_router
from .callbacks import router as callback_router

router = Router()
router.include_router(user_router)
router.include_router(callback_router)
