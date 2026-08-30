import re
import asyncio
import logging
import time
from collections import defaultdict
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.enums import ChatType
from aiogram.exceptions import TelegramNetworkError
from mediasave.app.database.database import get_session
from mediasave.app.database.repositories import UserRepository, UserSettingRepository, DownloadRepository
from mediasave.app.services.platform_detector import PlatformDetector
from mediasave.app.services.download_service import DownloadService
from mediasave.app.services.media_service import MediaService
from mediasave.app.services.queue import DownloadQueue, QueueFullError
from mediasave.app.downloaders.schemas import PlatformType, MediaType
from mediasave.app.i18n import get_text
from mediasave.app.config import settings
from mediasave.app.bot.utils import get_user_language
from pathlib import Path

router = Router()
logger = logging.getLogger(__name__)
platform_detector = PlatformDetector()

_user_rate_limits: dict[int, list[float]] = defaultdict(list)


def is_valid_url(text: str) -> bool:
    if not text:
        return False
    text = text.strip()
    pattern = re.compile(r"https?://[^\s]+", re.IGNORECASE)
    return bool(pattern.search(text))


def extract_url(text: str) -> str | None:
    if not text:
        return None
    match = re.search(r"https?://[^\s]+", text.strip())
    if match:
        return match.group(0)
    return None


def check_rate_limit(user_id: int) -> bool:
    now = time.time()
    window_start = now - 60.0
    timestamps = _user_rate_limits[user_id]
    _user_rate_limits[user_id] = [t for t in timestamps if t > window_start]
    if len(_user_rate_limits[user_id]) >= settings.rate_limit_per_minute:
        return False
    _user_rate_limits[user_id].append(now)
    return True


async def _send_media_with_retry(message: Message, file_path: str, media_type: str, caption: str, reply_markup, max_retries: int = 3):
    for attempt in range(max_retries + 1):
        try:
            if media_type == "photo":
                return await message.answer_photo(photo=FSInputFile(file_path), caption=caption, reply_markup=reply_markup)
            elif media_type == "document":
                return await message.answer_document(document=FSInputFile(file_path), caption=caption, reply_markup=reply_markup)
            elif media_type == "video_note":
                return await message.answer_video_note(video_note=FSInputFile(file_path))
            elif media_type == "audio":
                return await message.answer_audio(audio=FSInputFile(file_path), caption=caption, reply_markup=reply_markup)
            else:
                return await message.answer_video(video=FSInputFile(file_path), caption=caption, reply_markup=reply_markup)
        except (TelegramNetworkError, ConnectionResetError, asyncio.TimeoutError) as e:
            if attempt < max_retries:
                wait = min(2 ** attempt, 10)
                logger.warning("Send media failed (attempt %s/%s): %s. Retrying in %ss...", attempt + 1, max_retries + 1, e, wait)
                await asyncio.sleep(wait)
                continue
            logger.error("Send media failed after %s attempts: %s", max_retries + 1, e)
            raise


@router.message(lambda m: m.text and m.text == "/download")
async def cmd_download(message: Message):
    lang = await get_user_language(message)
    await message.answer(get_text(lang, "download_prompt"))


@router.message(lambda m: is_valid_url(m.text or ""))
async def handle_url(message: Message):
    url = extract_url(message.text or "")
    if not url:
        return

    chat_type = message.chat.type
    if chat_type in (ChatType.GROUP, ChatType.SUPERGROUP):
        if not message.text.lower().startswith(("/download", "download", "скачать", "yuklash")):
            return

    if not check_rate_limit(message.from_user.id):
        lang = await get_user_language(message)
        await message.answer(get_text(lang, "rate_limited"))
        return

    platform, downloader = platform_detector.detect(url)
    if platform == PlatformType.UNKNOWN or downloader is None:
        lang = await get_user_language(message)
        if "tiktok.com" in url.lower() or "vm.tiktok.com" in url.lower():
            await message.answer(get_text(lang, "tiktok_unsupported"))
        else:
            await message.answer(get_text(lang, "unsupported_platform"))
        return

    cookie_path = settings.platform_cookies_path(platform.value)
    logger.info("Download request: url=%s, platform=%s, cookies=%s", url, platform.value, cookie_path)

    download_id = None
    try:
        async with get_session() as session:
            user_repo = UserRepository(session)
            user = await user_repo.get_or_create(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
            )
            download_repo = DownloadRepository(session)
            download = await download_repo.create(user.id, url, platform, MediaType.UNKNOWN)
            download_id = download.id

        queue = DownloadQueue()
        try:
            position = queue.add(message.from_user.id)
            await message.answer(get_text("ru", "queue_position") + str(position))
        except QueueFullError:
            await message.answer(get_text("ru", "queue_full"))
            return

        async def do_download():
            nonlocal download_id
            lang = await get_user_language(message)
            status_msg = await message.answer(get_text(lang, "processing_url"))

            async def progress_callback(pct):
                try:
                    bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
                    await status_msg.edit_text(f"{get_text(lang, 'downloading')}\n\n{bar} {pct}%")
                except Exception:
                    pass

            try:
                temp_dir = settings.temp_path / f"user_{message.from_user.id}"
                service = DownloadService(downloader, temp_dir)
                file_path, info = await service.process(url, on_progress=progress_callback)

                if isinstance(file_path, list):
                    valid_files = [p for p in file_path if Path(p).is_file()]
                    if not valid_files:
                        await message.answer(get_text(lang, "content_unavailable"))
                        return
                    total = len(valid_files)
                    if total > 1:
                        await status_msg.edit_text(get_text(lang, "playlist_found").format(count=total))
                    else:
                        await status_msg.edit_text(get_text(lang, "carousel_found").format(count=total))
                    for idx, fp in enumerate(valid_files, 1):
                        try:
                            if total > 1:
                                await status_msg.edit_text(get_text(lang, "playlist_downloading").format(current=idx, total=total))
                            else:
                                await status_msg.edit_text(get_text(lang, "carousel_downloading").format(current=idx, total=total))
                            size = Path(fp).stat().st_size
                            if size > settings.max_file_size_mb * 1024 * 1024:
                                await message.answer(get_text(lang, "file_too_large"))
                                continue
                            if Path(fp).suffix.lower() in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
                                await message.answer_photo(photo=FSInputFile(fp), caption=f"{idx}/{total}")
                            elif Path(fp).suffix.lower() == ".webm":
                                await message.answer_document(document=FSInputFile(fp), caption=f"{idx}/{total}")
                            else:
                                await message.answer_video(video=FSInputFile(fp), caption=f"{idx}/{total}")
                        except Exception:
                            logger.exception("Failed to send item %s", fp)
                    kb = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text=get_text(lang, "actions_circle"), callback_data=f"act:circle:{download.id}")],
                        [InlineKeyboardButton(text=get_text(lang, "actions_mp3"), callback_data=f"act:mp3:{download.id}")],
                    ])
                    await message.answer(get_text(lang, "ready"), reply_markup=kb)
                    async with get_session() as session:
                        await DownloadRepository(session).update_status(download.id, "completed", file_path=valid_files[0])
                    return

                if not file_path or not Path(file_path).exists():
                    await message.answer(get_text(lang, "content_unavailable"))
                    return

                file_size = Path(file_path).stat().st_size
                if file_size > settings.max_file_size_mb * 1024 * 1024:
                    await message.answer(get_text(lang, "file_too_large"))
                    return

                media_service = MediaService(settings.temp_path / f"user_{message.from_user.id}")

                send_path = file_path
                is_video_file = info.media_type == MediaType.VIDEO and Path(file_path).suffix.lower() not in {".webm"}
                if is_video_file and file_size > 50 * 1024 * 1024:
                    try:
                        await status_msg.edit_text(get_text(lang, "downloading"))
                        compressed, error = await media_service.compress_video(file_path, max_size_mb=50)
                        if compressed and compressed != file_path:
                            send_path = compressed
                    except Exception:
                        send_path = file_path

                kb = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=get_text(lang, "actions_video"), callback_data=f"act:video:{download.id}")],
                    [InlineKeyboardButton(text=get_text(lang, "actions_circle"), callback_data=f"act:circle:{download.id}")],
                    [InlineKeyboardButton(text=get_text(lang, "actions_mp3"), callback_data=f"act:mp3:{download.id}")],
                    [InlineKeyboardButton(text=get_text(lang, "actions_thumbnail"), callback_data=f"act:thumb:{download.id}")],
                    [InlineKeyboardButton(text=get_text(lang, "actions_cut"), callback_data=f"act:cut:{download.id}")],
                ])

                sent = False
                logger.info("Sending file to user: path=%s, type=%s, size=%s", send_path, info.media_type, file_size)
                if info.media_type == MediaType.IMAGE:
                    try:
                        await message.answer_photo(photo=FSInputFile(send_path), caption=get_text(lang, "ready"), reply_markup=kb)
                        sent = True
                        logger.info("Sent photo successfully")
                    except Exception as e:
                        logger.exception("Failed to send photo: %s", e)
                        pass
                elif Path(send_path).suffix.lower() == ".webm":
                    try:
                        await message.answer_document(document=FSInputFile(send_path), caption=get_text(lang, "ready"), reply_markup=kb)
                        sent = True
                        logger.info("Sent webm document successfully")
                    except Exception as e:
                        logger.exception("Failed to send webm document: %s", e)
                        pass
                else:
                    try:
                        await message.answer_video(video=FSInputFile(send_path), caption=get_text(lang, "ready"), reply_markup=kb)
                        sent = True
                        logger.info("Sent video successfully")
                    except Exception as e:
                        logger.exception("Failed to send video: %s", e)
                        try:
                            await message.answer_document(document=FSInputFile(send_path), caption=get_text(lang, "ready"), reply_markup=kb)
                            sent = True
                            logger.info("Sent video as document successfully")
                        except Exception as e2:
                            logger.exception("Failed to send video as document: %s", e2)
                            pass

                if not sent:
                    await message.answer(get_text(lang, "download_error"))

            except Exception as e:
                error_str = str(e)
                try:
                    if "HTTP Error 403" in error_str or "403" in error_str:
                        await message.answer(get_text(lang, "content_protected"))
                        if platform == PlatformType.YOUTUBE:
                            cookie_path = settings.platform_cookies_path("youtube")
                            if not cookie_path:
                                await message.answer("Для скачивания YouTube может потребоваться авторизация. Загрузи cookies через /cookies_youtube.")
                    elif any(x in error_str.lower() for x in ["winerror 10054", "connectionreseterror", "forcibly closed", "handshake operation timed out", "timed out"]):
                        await message.answer(get_text(lang, "platform_blocked"))
                    else:
                        await message.answer(get_text(lang, "download_error"))
                except Exception:
                    logger.debug("Failed to send error message to user")
                logger.exception("Download handling failed for %s", url)
                try:
                    if download_id is not None:
                        async with get_session() as session:
                            await DownloadRepository(session).update_status(download_id, "failed", error_message=error_str[:500])
                except Exception:
                    logger.exception("Could not mark download %s as failed", download_id)
            finally:
                queue.remove(message.from_user.id)

        asyncio.create_task(do_download())

    except Exception:
        logger.exception("Download setup failed for %s", url)
        lang = await get_user_language(message)
        await message.answer(get_text(lang, "download_error"))
