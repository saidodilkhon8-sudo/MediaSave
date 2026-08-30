from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from mediasave.app.database.database import get_session
from mediasave.app.database.repositories import UserRepository, UserSettingRepository
from mediasave.app.i18n import get_text
from mediasave.app.config import settings
import logging

router = Router()
logger = logging.getLogger(__name__)


class CutStates(StatesGroup):
    waiting_for_cut = State()


def _settings_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(lang, "settings_language"), callback_data="set:lang")],
        [InlineKeyboardButton(text=get_text(lang, "settings_quality"), callback_data="set:quality")],
        [InlineKeyboardButton(text=get_text(lang, "settings_audio_format"), callback_data="set:audio")],
        [InlineKeyboardButton(text=get_text(lang, "settings_circle"), callback_data="set:circle")],
        [InlineKeyboardButton(text=get_text(lang, "settings_auto_delete"), callback_data="set:autodelete")],
        [InlineKeyboardButton(text=get_text(lang, "settings_watermark"), callback_data="set:watermark")],
    ])


@router.message(lambda m: m.text and (m.text == get_text("ru", "menu_settings") or m.text == get_text("en", "menu_settings") or m.text == get_text("uz", "menu_settings")))
async def open_settings(message: Message):
    async with get_session() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(message.from_user.id)
        lang = user.language if user else "ru"
    text = get_text(lang, "settings_title")
    kb = _settings_keyboard(lang)
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == "set:lang")
async def set_language(callback: CallbackQuery):
    async with get_session() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(callback.from_user.id)
        lang = user.language if user else "ru"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru")],
        [InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang:uz")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en")],
    ])
    await callback.message.edit_text(get_text(lang, "settings_language"), reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data.startswith("lang:"))
async def change_language(callback: CallbackQuery):
    new_lang = callback.data.split(":")[1]
    async with get_session() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(callback.from_user.id)
        if user:
            await user_repo.set_language(user.id, new_lang)
    await callback.message.edit_text(get_text(new_lang, "settings_title"), reply_markup=_settings_keyboard(new_lang))
    await callback.answer()


@router.callback_query(F.data == "set:quality")
async def choose_quality(callback: CallbackQuery):
    async with get_session() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(callback.from_user.id)
        lang = user.language if user else "ru"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Best", callback_data="quality:best")],
        [InlineKeyboardButton(text="1080p", callback_data="quality:1080")],
        [InlineKeyboardButton(text="720p", callback_data="quality:720")],
        [InlineKeyboardButton(text="480p", callback_data="quality:480")],
        [InlineKeyboardButton(text="360p", callback_data="quality:360")],
    ])
    await callback.message.edit_text(get_text(lang, "settings_quality"), reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data.startswith("quality:"))
async def change_quality(callback: CallbackQuery):
    quality = callback.data.split(":", 1)[1]
    async with get_session() as session:
        user_repo = UserRepository(session)
        setting_repo = UserSettingRepository(session)
        user = await user_repo.get_by_telegram_id(callback.from_user.id)
        if user:
            await setting_repo.set(user.id, "quality", quality)
            lang = user.language or "ru"
        else:
            lang = "ru"
    await callback.message.edit_text(get_text(lang, "settings_title"), reply_markup=_settings_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data == "set:watermark")
async def toggle_watermark(callback: CallbackQuery):
    async with get_session() as session:
        user = await UserRepository(session).get_by_telegram_id(callback.from_user.id)
        if not user:
            await callback.answer(get_text("ru", "download_error"), show_alert=True)
            return
        repository = UserSettingRepository(session)
        current = await repository.get(user.id, "watermark_enabled")
        enabled = current != "false"
        await repository.set(user.id, "watermark_enabled", "false" if enabled else "true")
        lang = user.language or "ru"
    await callback.answer(get_text(lang, "watermark_off" if enabled else "watermark_on"), show_alert=True)
    await callback.message.edit_reply_markup(reply_markup=_settings_keyboard(lang))


@router.callback_query(F.data.in_({"set:quality", "set:audio", "set:circle", "set:autodelete"}))
async def settings_coming_soon(callback: CallbackQuery):
    async with get_session() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(callback.from_user.id)
        lang = user.language if user else "ru"
    try:
        await callback.answer(get_text(lang, "download_error"), show_alert=True)
    except Exception:
        pass
