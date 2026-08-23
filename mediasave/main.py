import asyncio
import logging
import shutil
from pathlib import Path
from datetime import datetime, timedelta, timezone
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from mediasave.app.bot import router as bot_router
from mediasave.app.database.database import engine
from mediasave.app.database.models import Base
from mediasave.app.config import settings

logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
logger = logging.getLogger(__name__)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def cleanup_temp_files():
    while True:
        try:
            cutoff = datetime.now(timezone.utc) - timedelta(hours=settings.auto_delete_hours)
            for user_dir in settings.temp_path.iterdir():
                if user_dir.is_dir():
                    for item in user_dir.iterdir():
                        if item.stat().st_mtime < cutoff.timestamp():
                            if item.is_dir():
                                shutil.rmtree(item, ignore_errors=True)
                            else:
                                item.unlink(missing_ok=True)
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
        await asyncio.sleep(3600)


async def main():
    await init_db()
    settings.temp_path.mkdir(parents=True, exist_ok=True)
    asyncio.create_task(cleanup_temp_files())
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_router(bot_router)
    logger.info("MediaSave bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
