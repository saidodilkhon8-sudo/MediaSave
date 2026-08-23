from aiogram import Router
from .handlers import start, download, media_actions, settings, history, cutter
from .keyboards import router as keyboards_router

router = Router()
router.include_router(start.router)
router.include_router(download.router)
router.include_router(media_actions.router)
router.include_router(settings.router)
router.include_router(history.router)
router.include_router(cutter.router)
