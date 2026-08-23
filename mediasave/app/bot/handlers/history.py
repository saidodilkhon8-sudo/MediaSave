from aiogram import Router, F
from aiogram.types import Message
from mediasave.app.database.database import get_session
from mediasave.app.database.repositories import UserRepository, DownloadRepository
from mediasave.app.i18n import get_text

router = Router()


@router.message(lambda m: m.text and (m.text == get_text("ru", "menu_history") or m.text == get_text("en", "menu_history") or m.text == get_text("uz", "menu_history")))
async def show_history(message: Message):
    async with get_session() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(message.from_user.id)
        lang = user.language if user else "ru"
        download_repo = DownloadRepository(session)
        downloads = await download_repo.get_recent_by_user(message.from_user.id)

    if not downloads:
        await message.answer(get_text(lang, "history_empty"))
        return

    lines = []
    for i, d in enumerate(downloads[:10], 1):
        lines.append(f"{i}. {d.platform} — {d.created_at.strftime('%d.%m.%Y')}")
    await message.answer(get_text(lang, "history_title") + "\n\n" + "\n".join(lines))
