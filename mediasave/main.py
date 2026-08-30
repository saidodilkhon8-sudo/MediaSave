import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramNetworkError
from mediasave.app.config import settings
from mediasave.app.database.database import init_db, close_db
from mediasave.app.services.cleanup_service import cleanup_temp_files
from mediasave.app.bot.handlers.start import router as start_router
from mediasave.app.bot.handlers.download import router as download_router
from mediasave.app.bot.handlers.media_actions import router as media_actions_router
from mediasave.app.bot.handlers.settings import router as settings_router
from mediasave.app.bot.handlers.history import router as history_router
from mediasave.app.bot.handlers.music_search import router as music_search_router
from mediasave.app.bot.handlers.admin import router as admin_router


logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


class ResilientTelegramSession(AiohttpSession):
    async def make_request(self, bot, method, timeout=None):
        last_error = None
        for attempt in range(4):
            try:
                return await super().make_request(bot, method, timeout=timeout)
            except (TelegramNetworkError, ConnectionResetError, asyncio.TimeoutError) as error:
                last_error = error
                if attempt == 3:
                    raise
                delay = min(2 ** attempt, 8)
                logger.warning("Telegram request failed, retrying in %ss: %s", delay, error)
                await asyncio.sleep(delay)
        raise last_error


def _handle_exception(loop, context):
    msg = context.get("exception", context.get("message", ""))
    if isinstance(msg, (ConnectionResetError, TimeoutError, asyncio.CancelledError)):
        return
    logger.debug("Asyncio background task error: %s", msg)


async def main():
    if not settings.bot_token:
        logger.error("BOT_TOKEN is not set")
        sys.exit(1)

    await init_db()

    loop = asyncio.get_running_loop()
    loop.set_exception_handler(_handle_exception)

    session = ResilientTelegramSession(timeout=120, proxy=settings.proxy_url or None)

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        session=session,
    )
    dp = Dispatcher()
    dp.include_router(start_router)
    dp.include_router(download_router)
    dp.include_router(media_actions_router)
    dp.include_router(settings_router)
    dp.include_router(music_search_router)
    dp.include_router(history_router)
    dp.include_router(admin_router)

    asyncio.create_task(cleanup_temp_files())

    try:
        attempt = 0
        while True:
            try:
                await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
                break
            except (TelegramNetworkError, ConnectionResetError, asyncio.TimeoutError) as error:
                attempt += 1
                delay = min(5 * attempt, 30)
                logger.warning("Polling attempt %s failed: %s. Retrying in %ss", attempt, error, delay)
                await asyncio.sleep(delay)
    finally:
        await close_db()
        try:
            await bot.session.close()
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())
