from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from mediasave.app.database.database import get_session
from mediasave.app.database.models import Download
from mediasave.app.database.repositories import DownloadRepository, UserRepository
from mediasave.app.services.media_service import MediaService
from mediasave.app.i18n import get_text
from mediasave.app.config import settings
from pathlib import Path

router = Router()


@router.callback_query(F.data.startswith("act:"))
async def handle_action(callback: CallbackQuery):
    async with get_session() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(callback.from_user.id)
        lang = user.language if user else "ru"

    parts = callback.data.split(":")
    action = parts[1]
    download_id = int(parts[2])

    async with get_session() as session:
        download = await session.get(Download, download_id)

    if not download or not download.file_path:
        await callback.answer(get_text(lang, "content_unavailable"), show_alert=True)
        return

    media_service = MediaService(settings.temp_path / f"user_{callback.from_user.id}")
    input_path = download.file_path

    try:
        if action == "circle":
            await callback.answer(get_text(lang, "creating_circle"))
            output, error = await media_service.create_circle(input_path)
            if output and Path(output).exists():
                await callback.message.answer_video_note(video_note=FSInputFile(output))
                await callback.message.answer(get_text(lang, "ready"))
            else:
                await callback.answer(error or get_text(lang, "download_error"), show_alert=True)

        elif action == "mp3":
            await callback.answer(get_text(lang, "creating_mp3"))
            output, error = await media_service.create_mp3(input_path)
            if output and Path(output).exists():
                await callback.message.answer_audio(audio=FSInputFile(output))
                await callback.message.answer(get_text(lang, "ready"))
            else:
                await callback.answer(error or get_text(lang, "download_error"), show_alert=True)

        elif action == "thumb":
            await callback.answer(get_text(lang, "creating_thumbnail"))
            output, error = await media_service.create_thumbnail(input_path)
            if output and Path(output).exists():
                await callback.message.answer_photo(photo=FSInputFile(output))
                await callback.message.answer(get_text(lang, "ready"))
            else:
                await callback.answer(error or get_text(lang, "download_error"), show_alert=True)

        elif action == "cut":
            await callback.message.answer(get_text(lang, "cut_prompt"))
            await callback.answer()
            return

        elif action == "video":
            if Path(input_path).exists():
                await callback.message.answer_video(video=FSInputFile(input_path))
            else:
                await callback.answer(get_text(lang, "content_unavailable"), show_alert=True)

        await callback.answer()
    except Exception:
        await callback.answer(get_text(lang, "download_error"), show_alert=True)
