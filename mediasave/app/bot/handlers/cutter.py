import re
from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from mediasave.app.database.database import get_session
from mediasave.app.database.repositories import DownloadRepository
from mediasave.app.services.media_service import MediaService
from mediasave.app.i18n import get_text
from mediasave.app.config import settings

router = Router()


@router.message(lambda m: m.text and m.text.startswith("/cut "))
async def handle_cut(message: Message):
    async with get_session() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(message.from_user.id)
        lang = user.language if user else "ru"
    parts = message.text.strip().split()
    if len(parts) != 3:
        await message.answer(get_text(lang, "cut_invalid"))
        return

    try:
        start = _parse_time(parts[1])
        end = _parse_time(parts[2])
    except ValueError:
        await message.answer(get_text(lang, "cut_invalid"))
        return

    if start >= end:
        await message.answer(get_text(lang, "cut_invalid_range"))
        return

    async with get_session() as session:
        download_repo = DownloadRepository(session)
        downloads = await download_repo.get_recent_by_user(message.from_user.id, limit=1)
        if not downloads:
            await message.answer(get_text(lang, "download_error"))
            return
        download = downloads[0]

    if not download.file_path:
        await message.answer(get_text(lang, "download_error"))
        return

    media_service = MediaService(settings.temp_path / f"user_{message.from_user.id}")
    output, error = await media_service.cut_video(download.file_path, start, end)
    if output:
        await message.answer_video(video=FSInputFile(output), caption=get_text(lang, "ready"))
    else:
        await message.answer(get_text(lang, "download_error"))


def _parse_time(time_str: str) -> float:
    parts = time_str.split(":")
    if len(parts) != 3:
        raise ValueError("Invalid time format")
    h, m, s = map(int, parts)
    return h * 3600 + m * 60 + s
