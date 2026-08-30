import logging
from pathlib import Path
from typing import Optional, Dict, List
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from mediasave.app.i18n import get_text
from mediasave.app.bot.utils import get_user_language
from mediasave.app.services.music_search import MusicSearchService

router = Router()
logger = logging.getLogger(__name__)
music_search = MusicSearchService()

PAGE_SIZE = 10
_pending_results: Dict[int, List[Dict]] = {}
_pending_pages: Dict[int, int] = {}


def _get_user_state(user_id: int) -> Dict:
    return {
        "results": _pending_results.get(user_id, []),
        "page": _pending_pages.get(user_id, 0),
    }


def _set_user_state(user_id: int, results: List[Dict], page: int = 0) -> None:
    _pending_results[user_id] = results
    _pending_pages[user_id] = page


def _clear_user_state(user_id: int) -> None:
    _pending_results.pop(user_id, None)
    _pending_pages.pop(user_id, None)


def _build_music_keyboard(lang: str, results: List[Dict], page: int) -> InlineKeyboardMarkup:
    start = page * PAGE_SIZE
    end = min(start + PAGE_SIZE, len(results))
    rows = []
    for idx in range(start, end):
        item = results[idx]
        title = item.get("title") or "Unknown"
        artist = item.get("uploader") or "Unknown"
        label = f"{artist} - {title}"
        rows.append([InlineKeyboardButton(text=label, callback_data=f"music_select:{idx}")])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="<-----назад", callback_data=f"music_page:{page-1}"))
    if end < len(results):
        nav.append(InlineKeyboardButton(text="далее----->", callback_data=f"music_page:{page+1}"))
    if nav:
        rows.append(nav)
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.message(lambda m: m.text and (
    m.text == get_text("ru", "menu_music_search") or
    m.text == get_text("en", "menu_music_search") or
    m.text == get_text("uz", "menu_music_search")
))
async def prompt_music_search(message: Message):
    lang = await get_user_language(message)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(lang, "music_search_by_artist"), callback_data="music_search:artist")],
        [InlineKeyboardButton(text=get_text(lang, "music_search_by_track"), callback_data="music_search:track")],
    ])
    await message.answer(get_text(lang, "music_search_prompt"), reply_markup=kb)


@router.callback_query(F.data == "music_search:artist")
async def music_search_artist(callback: CallbackQuery):
    lang = await get_user_language(callback.message)
    _set_user_state(callback.from_user.id, [], 0)
    await callback.answer()
    await callback.message.answer(get_text(lang, "music_search_artist_prompt"))


@router.callback_query(F.data == "music_search:track")
async def music_search_track(callback: CallbackQuery):
    lang = await get_user_language(callback.message)
    _set_user_state(callback.from_user.id, [], 0)
    await callback.answer()
    await callback.message.answer(get_text(lang, "music_search_track_prompt"))


@router.message(lambda m: m.chat.type == ChatType.PRIVATE and bool(m.text))
async def handle_music_search_text(message: Message):
    user_id = message.from_user.id
    if user_id not in _pending_results:
        return
    lang = await get_user_language(message)
    query = message.text.strip()
    status_msg = await message.answer("⏳ Ищу музыку...")
    results = await music_search.search(query)
    if not results:
        await _safe_edit(status_msg, get_text(lang, "music_search_not_found"))
        _clear_user_state(user_id)
        return
    _set_user_state(user_id, results, 0)
    kb = _build_music_keyboard(lang, results, 0)
    await _safe_edit(status_msg, "⏳ Результаты:", reply_markup=kb)


@router.callback_query(lambda c: c.data.startswith("music_page:"))
async def music_search_page(callback: CallbackQuery):
    user_id = callback.from_user.id
    state = _get_user_state(user_id)
    if not state["results"]:
        await callback.answer()
        return
    page = int(callback.data.split(":")[1])
    _set_user_state(user_id, state["results"], page)
    lang = await get_user_language(callback.message)
    kb = _build_music_keyboard(lang, state["results"], page)
    try:
        await callback.message.edit_reply_markup(reply_markup=kb)
    except TelegramBadRequest:
        pass
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("music_select:"))
async def music_search_select(callback: CallbackQuery):
    user_id = callback.from_user.id
    state = _get_user_state(user_id)
    idx = int(callback.data.split(":")[1])
    if not state["results"] or idx >= len(state["results"]):
        await callback.answer()
        return
    item = state["results"][idx]
    lang = await get_user_language(callback.message)
    await callback.answer("⏳ Загружаю...")
    result = await music_search.download_track(item["url"])
    _clear_user_state(user_id)
    if not result:
        await callback.message.answer(get_text(lang, "music_search_error"))
        return
    try:
        audio = FSInputFile(result["path"])
        title = result.get("title") or item.get("title") or "Unknown"
        artist = result.get("uploader") or item.get("uploader") or "Unknown"
        duration = result.get("duration") or item.get("duration")
        duration_str = f"{duration // 60}:{duration % 60:02d}" if isinstance(duration, int) else "?:??"
        caption = get_text(lang, "music_search_result").format(title=title, artist=artist, duration=duration_str)
        await callback.message.answer_audio(audio, title=title, performer=artist, caption=caption, parse_mode=ParseMode.HTML)
    except Exception:
        logger.exception("Music search send failed")
        await callback.message.answer(get_text(lang, "music_search_error"))
    finally:
        try:
            Path(result.get("path", "")).unlink(missing_ok=True)
        except Exception:
            pass


async def _safe_edit(message: Optional[Message], text: str, reply_markup=None) -> None:
    if not message:
        return
    try:
        await message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest:
        pass
    except Exception:
        pass


async def _safe_reply(message: Message, text: str) -> None:
    try:
        await message.answer(text)
    except Exception:
        pass


async def _safe_delete(message: Optional[Message]) -> None:
    if not message:
        return
    try:
        await message.delete()
    except TelegramBadRequest:
        pass
    except Exception:
        pass
