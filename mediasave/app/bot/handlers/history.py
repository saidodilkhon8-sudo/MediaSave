import logging
from aiogram import Router
from aiogram.types import Message
from mediasave.app.database.database import get_session
from mediasave.app.database.repositories import UserRepository, DownloadRepository
from mediasave.app.i18n import get_text
from mediasave.app.bot.utils import get_user_language

router = Router()
logger = logging.getLogger(__name__)


@router.message(lambda m: m.text and (
    m.text == get_text("ru", "menu_history") or
    m.text == get_text("en", "menu_history") or
    m.text == get_text("uz", "menu_history")
))
async def show_history(message: Message):
    lang = await get_user_language(message)
    async with get_session() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(message.from_user.id)
        if not user:
            await message.answer(get_text(lang, "history_empty"))
            return
        download_repo = DownloadRepository(session)
        downloads = await download_repo.get_user_history(user.id, limit=20)

    if not downloads:
        await message.answer(get_text(lang, "history_empty"))
        return

    lines = [get_text(lang, "history_title")]
    platform_map = {
        "instagram": "📸 Instagram",
        "youtube": "▶️ YouTube",
        "youtube_shorts": "▶️ YouTube Shorts",
        "twitter": "🐦 Twitter",
        "facebook": "📘 Facebook",
        "reddit": "🧵 Reddit",
        "pinterest": "📌 Pinterest",
        "snapchat": "👻 Snapchat",
        "likee": "🎮 Likee",
        "threads": "🧵 Threads",
    }

    for d in downloads:
        emoji = platform_map.get(d.platform.value, "🌐")
        lines.append(f"{emoji} {d.url[:50]}")

    await message.answer("\n".join(lines))
