import time
import re
from collections import defaultdict
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from mediasave.app.database.database import get_session
from mediasave.app.database.models import Download
from mediasave.app.database.repositories import DownloadRepository, UserRepository
from mediasave.app.services.media_service import MediaService
from mediasave.app.i18n import get_text
from mediasave.app.config import settings
from pathlib import Path
import logging

router = Router()
logger = logging.getLogger(__name__)


class CutStates(StatesGroup):
    waiting_for_range = State()

_user_rate_limits: dict[int, list[float]] = defaultdict(list)


def check_rate_limit(user_id: int) -> bool:
    now = time.time()
    window_start = now - 60.0
    timestamps = _user_rate_limits[user_id]
    _user_rate_limits[user_id] = [t for t in timestamps if t > window_start]
    if len(_user_rate_limits[user_id]) >= settings.rate_limit_per_minute:
        return False
    _user_rate_limits[user_id].append(now)
    return True


@router.callback_query(F.data.startswith("act:"))
async def handle_action(callback: CallbackQuery, state: FSMContext):
    if not check_rate_limit(callback.from_user.id):
        await callback.answer(get_text("ru", "rate_limited"), show_alert=True)
        return

    parts = callback.data.split(":")
    if len(parts) != 3:
        await callback.answer(get_text("ru", "download_error"), show_alert=True)
        return

    action = parts[1]
    try:
        download_id = int(parts[2])
    except ValueError:
        await callback.answer(get_text("ru", "download_error"), show_alert=True)
        return

    async with get_session() as session:
        download = await session.get(Download, download_id)

    if not download or not download.file_path:
        await callback.answer(get_text("ru", "content_unavailable"), show_alert=True)
        return

    user_lang = "ru"
    async with get_session() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(callback.from_user.id)
        if not user or download.user_id != user.id:
            await callback.answer(get_text("ru", "content_unavailable"), show_alert=True)
            return
        user_lang = user.language or "ru"

    try:
        await callback.answer()
    except Exception:
        pass

    media_service = MediaService(settings.temp_path / f"user_{callback.from_user.id}")
    input_path = download.file_path

    async def _progress(text_key):
        try:
            await callback.message.answer(get_text(user_lang, text_key))
        except Exception:
            pass

    try:
        if action == "circle":
            await _progress("creating_circle")
            output, error = await media_service.create_circle(input_path)
            if output and Path(output).exists():
                await callback.message.answer_video_note(video_note=FSInputFile(output))
                await callback.message.answer(get_text(user_lang, "ready"))
            else:
                await callback.message.answer(error or get_text(user_lang, "download_error"))

        elif action == "video":
            if Path(input_path).suffix.lower() in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
                await callback.message.answer(get_text(user_lang, "download_error"))
            elif Path(input_path).suffix.lower() == ".webm":
                await callback.message.answer_document(document=FSInputFile(input_path))
            else:
                await callback.message.answer_video(video=FSInputFile(input_path))
                await callback.message.answer(get_text(user_lang, "ready"))

        elif action == "mp3":
            await _progress("creating_mp3")
            output, error = await media_service.create_mp3(input_path)
            if output and Path(output).exists():
                await callback.message.answer_audio(audio=FSInputFile(output))
                await callback.message.answer(get_text(user_lang, "ready"))
            else:
                await callback.message.answer(error or get_text(user_lang, "download_error"))

        elif action == "thumb":
            await _progress("creating_thumbnail")
            output, error = await media_service.create_thumbnail(input_path)
            if output and Path(output).exists():
                await callback.message.answer_photo(photo=FSInputFile(output))
                await callback.message.answer(get_text(user_lang, "ready"))
            else:
                await callback.message.answer(error or get_text(user_lang, "download_error"))

        elif action == "cut":
            await state.update_data(input_path=input_path)
            await state.set_state(CutStates.waiting_for_range)
            await callback.message.answer(get_text(user_lang, "cut_prompt"))
    except Exception as e:
        logger.exception("Media action failed: %s", e)
        try:
            await callback.message.answer(get_text("ru", "download_error"))
        except Exception:
            pass


def _parse_time(value: str) -> int | None:
    parts = value.strip().split(":")
    if not 1 <= len(parts) <= 3 or not all(part.isdigit() for part in parts):
        return None
    numbers = [int(part) for part in parts]
    if len(numbers) == 1:
        return numbers[0]
    if len(numbers) == 2 and numbers[1] < 60:
        return numbers[0] * 60 + numbers[1]
    if len(numbers) == 3 and numbers[1] < 60 and numbers[2] < 60:
        return numbers[0] * 3600 + numbers[1] * 60 + numbers[2]
    return None


@router.message(CutStates.waiting_for_range)
async def handle_cut_range(message: Message, state: FSMContext):
    if (message.text or "").strip().lower() in {"/cancel", "отмена", "cancel"}:
        await state.clear()
        await message.answer("Обрезка отменена.")
        return

    values = re.split(r"\s+|[-–—]", (message.text or "").strip())
    if len(values) != 2:
        await message.answer("Укажи начало и конец через пробел: 00:00 00:30")
        return

    start = _parse_time(values[0])
    end = _parse_time(values[1])
    if start is None or end is None or start >= end:
        await message.answer("Неверный диапазон. Пример: 00:00 00:30")
        return

    data = await state.get_data()
    input_path = data.get("input_path")
    await state.clear()
    if not input_path or not Path(input_path).is_file():
        await message.answer(get_text("ru", "content_unavailable"))
        return

    try:
        service = MediaService(settings.temp_path / f"user_{message.from_user.id}")
        output, error = await service.cut_video(input_path, str(start), str(end))
        if output and Path(output).is_file():
            await message.answer_video(video=FSInputFile(output), caption=get_text("ru", "ready"))
        else:
            await message.answer(error or get_text("ru", "download_error"))
    except Exception:
        logger.exception("Cut action failed")
        await message.answer(get_text("ru", "download_error"))
