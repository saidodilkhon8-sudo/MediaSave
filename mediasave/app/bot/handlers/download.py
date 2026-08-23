import re
import asyncio
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from mediasave.app.database.database import get_session
from mediasave.app.database.repositories import UserRepository, UserSettingRepository, DownloadRepository
from mediasave.app.services.platform_detector import PlatformDetector
from mediasave.app.services.download_service import DownloadService
from mediasave.app.services.media_service import MediaService
from mediasave.app.services.queue import DownloadQueue
from mediasave.app.downloaders.schemas import PlatformType, MediaType
from mediasave.app.i18n import get_text
from mediasave.app.config import settings
from pathlib import Path

router = Router()
logger = logging.getLogger(__name__)
platform_detector = PlatformDetector()
download_queue = DownloadQueue()


def is_valid_url(text: str) -> bool:
    return bool(re.match(r"^https?://", text.strip()))


@router.message(lambda m: is_valid_url(m.text or ""))
async def handle_url(message: Message):
    url = message.text.strip()
    async with get_session() as session:
        user_repo = UserRepository(session)
        setting_repo = UserSettingRepository(session)
        user = await user_repo.get_or_create(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
        )
        lang = user.language or "ru"
        quality = await setting_repo.get(user.id, "quality") or "best"

        download_repo = DownloadRepository(session)
        download = await download_repo.create(
            user_id=user.id, url=url, platform="unknown", media_type="unknown"
        )

    platform, downloader = platform_detector.detect(url)
    if not downloader:
        await message.answer(get_text(lang, "unsupported_platform"))
        return

    async with get_session() as session:
        download_repo = DownloadRepository(session)
        await download_repo.update_status(download.id, "processing")

    queue_size = download_queue.size
    if queue_size >= settings.max_queue_size:
        await message.answer(get_text(lang, "queue_position") + str(queue_size + 1))
        return

    async def do_download():
        status_msg = await message.answer(get_text(lang, "downloading"))

        async def progress_callback(pct):
            try:
                bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
                await status_msg.edit_text(f"{get_text(lang, 'downloading')}\n\n{bar} {pct}%")
            except Exception:
                pass

        try:
            temp_dir = settings.temp_path / f"user_{message.from_user.id}"
            service = DownloadService(downloader, temp_dir)
            file_path, info = await service.process(url, on_progress=progress_callback, quality=quality)

            if not file_path or not Path(file_path).exists():
                await message.answer(get_text(lang, "content_unavailable"))
                return

            async with get_session() as session:
                download_repo = DownloadRepository(session)
                await download_repo.update_status(download.id, "completed", file_path=file_path)

            file_size = Path(file_path).stat().st_size
            if file_size > settings.max_file_size_mb * 1024 * 1024:
                await message.answer(get_text(lang, "file_too_large"))
                return

            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text(lang, "actions_video"), callback_data=f"act:video:{download.id}")],
                [InlineKeyboardButton(text=get_text(lang, "actions_circle"), callback_data=f"act:circle:{download.id}")],
                [InlineKeyboardButton(text=get_text(lang, "actions_mp3"), callback_data=f"act:mp3:{download.id}")],
                [InlineKeyboardButton(text=get_text(lang, "actions_thumbnail"), callback_data=f"act:thumb:{download.id}")],
                [InlineKeyboardButton(text=get_text(lang, "actions_cut"), callback_data=f"act:cut:{download.id}")],
            ])

            if info.media_type == MediaType.IMAGE:
                await message.answer_photo(photo=FSInputFile(file_path), caption=get_text(lang, "ready"), reply_markup=kb)
            elif Path(file_path).suffix.lower() == ".webm":
                await message.answer_document(document=FSInputFile(file_path), caption=get_text(lang, "ready"), reply_markup=kb)
            else:
                await message.answer_video(video=FSInputFile(file_path), caption=get_text(lang, "ready"), reply_markup=kb)

        except Exception:
            logger.exception("Download handling failed for %s", url)
            await message.answer(get_text(lang, "download_error"))
            try:
                async with get_session() as session:
                    download_repo = DownloadRepository(session)
                    await download_repo.update_status(download.id, "failed", error_message="error")
            except Exception:
                logger.exception("Could not mark download %s as failed", download.id)

    position = await download_queue.enqueue(do_download)
    if position > 1:
        await message.answer(get_text(lang, "queue_position") + str(position))
