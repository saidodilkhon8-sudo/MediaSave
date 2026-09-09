import asyncio
import logging
import os
import threading
from fastapi import FastAPI
from starlette.responses import JSONResponse

logging.basicConfig(
    level=getattr(logging, os.environ.get("LOG_LEVEL", "INFO").upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("vercel")

startup_lock = threading.Lock()
bot_started = False


def _run_bot():
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from mediasave.main import main as bot_main
        asyncio.run(bot_main())
    except Exception as e:
        logger.error("Bot failed: %s", e)
        raise


def _start_bot_background():
    global bot_started
    with startup_lock:
        if bot_started:
            return
        if not os.environ.get("BOT_TOKEN"):
            logger.warning("BOT_TOKEN not set; bot will not start")
            return
        thread = threading.Thread(target=_run_bot, daemon=True, name="telegram-bot")
        thread.start()
        bot_started = True
        logger.info("Telegram bot started in background thread")


app = FastAPI(title="MediaSave Bot")

_start_bot_background()


@app.get("/health")
async def health():
    return JSONResponse({"status": "ok", "bot_started": bot_started})


@app.get("/")
async def root():
    return JSONResponse({"status": "running", "service": "mediasave-bot"})
