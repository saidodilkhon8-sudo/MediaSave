from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from mediasave.app.i18n import get_text


def settings_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(lang, "settings_language"), callback_data="set:lang")],
        [InlineKeyboardButton(text=get_text(lang, "settings_quality"), callback_data="set:quality")],
        [InlineKeyboardButton(text=get_text(lang, "settings_audio_format"), callback_data="set:audio")],
        [InlineKeyboardButton(text=get_text(lang, "settings_circle"), callback_data="set:circle")],
        [InlineKeyboardButton(text=get_text(lang, "settings_auto_delete"), callback_data="set:autodelete")],
    ])


def language_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru")],
        [InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang:uz")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en")],
    ])


def quality_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Best", callback_data="quality:best")],
        [InlineKeyboardButton(text="1080p", callback_data="quality:1080")],
        [InlineKeyboardButton(text="720p", callback_data="quality:720")],
        [InlineKeyboardButton(text="480p", callback_data="quality:480")],
        [InlineKeyboardButton(text="360p", callback_data="quality:360")],
    ])
