from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from mediasave.app.i18n import get_text


def media_actions_keyboard(lang: str, download_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(lang, "actions_video"), callback_data=f"act:video:{download_id}")],
        [InlineKeyboardButton(text=get_text(lang, "actions_circle"), callback_data=f"act:circle:{download_id}")],
        [InlineKeyboardButton(text=get_text(lang, "actions_mp3"), callback_data=f"act:mp3:{download_id}")],
        [InlineKeyboardButton(text=get_text(lang, "actions_thumbnail"), callback_data=f"act:thumb:{download_id}")],
        [InlineKeyboardButton(text=get_text(lang, "actions_cut"), callback_data=f"act:cut:{download_id}")],
    ])
