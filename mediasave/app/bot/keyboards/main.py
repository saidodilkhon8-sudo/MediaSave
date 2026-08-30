from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from mediasave.app.i18n import get_text


def main_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(lang, "menu_download"), callback_data="menu:download")],
        [InlineKeyboardButton(text=get_text(lang, "menu_music_search"), callback_data="menu:music_search")],
        [InlineKeyboardButton(text=get_text(lang, "menu_history"), callback_data="menu:history")],
        [InlineKeyboardButton(text=get_text(lang, "menu_settings"), callback_data="menu:settings")],
        [InlineKeyboardButton(text=get_text(lang, "menu_help"), callback_data="menu:help")],
    ])
