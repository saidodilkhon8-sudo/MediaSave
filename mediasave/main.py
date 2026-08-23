import asyncio
import logging
import shutil
import os
from pathlib import Path
from datetime import datetime, timedelta, timezone
from aiohttp import web
from aiogram.types import Update
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


async def health_check(request: web.Request) -> web.Response:
    return web.json_response({"status": "ok"})


async def start_health_server(bot: Bot, dp: Dispatcher) -> web.AppRunner:
    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)

    async def telegram_webhook(request: web.Request) -> web.Response:
        try:
            update = Update.model_validate(await request.json())
            await dp.feed_update(bot, update)
            return web.json_response({"ok": True})
        except Exception:
            logger.exception("Telegram webhook update failed")
            return web.json_response({"ok": False}, status=500)

    app.router.add_post("/telegram/webhook", telegram_webhook)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", "10000")))
    await site.start()
    return runner


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
    health_runner = await start_health_server(bot, dp)
    logger.info("MediaSave bot started")
    try:
        render_host = os.getenv("RENDER_EXTERNAL_HOSTNAME")
        if render_host:
            webhook_url = f"https://{render_host}/telegram/webhook"
            await bot.set_webhook(webhook_url, drop_pending_updates=True)
            logger.info("Webhook mode enabled: %s", webhook_url)
            await asyncio.Event().wait()
        else:
            await bot.delete_webhook(drop_pending_updates=True)
            logger.info("Local polling mode enabled")
            await dp.start_polling(bot)
    finally:
        if os.getenv("RENDER_EXTERNAL_HOSTNAME"):
            await bot.delete_webhook()
        await health_runner.cleanup()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
