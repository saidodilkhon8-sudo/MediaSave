import os
import logging
from pathlib import Path
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from mediasave.app.i18n import get_text
from mediasave.app.config import settings
from mediasave.app.bot.utils import get_user_language
from mediasave.app.database.database import get_session
from mediasave.app.database.repositories import UserRepository

router = Router()
logger = logging.getLogger(__name__)


def _looks_like_cookies(text: str) -> bool:
    return ".youtube.com" in text and "SID" in text


def _detect_platform(text: str) -> str:
    lowered = text.lower()
    if ".youtube.com" in lowered or "youtube.com" in lowered:
        return "youtube"
    if "instagram.com" in lowered or "instagr.am" in lowered:
        return "instagram"
    if "twitter.com" in lowered or "x.com" in lowered:
        return "twitter"
    if "facebook.com" in lowered or "fb.watch" in lowered:
        return "facebook"
    return "generic"


@router.message(CommandStart())
async def cmd_start(message: Message):
    async with get_session() as session:
        user_repo = UserRepository(session)
        await user_repo.get_or_create(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
        )
    lang = await get_user_language(message)
    text = get_text(lang, "start_message")
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text(lang, "menu_download"))],
            [KeyboardButton(text=get_text(lang, "menu_music_search")), KeyboardButton(text=get_text(lang, "menu_history"))],
            [KeyboardButton(text=get_text(lang, "menu_settings")), KeyboardButton(text=get_text(lang, "menu_help"))],
        ],
        resize_keyboard=True,
    )
    await message.answer(text, reply_markup=kb)


@router.message(lambda m: m.text and m.text in {
    get_text("ru", "menu_download"),
    get_text("uz", "menu_download"),
    get_text("en", "menu_download"),
})
async def menu_download(message: Message):
    lang = await get_user_language(message)
    await message.answer(get_text(lang, "download_prompt"))


@router.message(lambda m: m.text and m.text in {
    get_text("ru", "menu_help"),
    get_text("uz", "menu_help"),
    get_text("en", "menu_help"),
})
async def menu_help(message: Message):
    lang = await get_user_language(message)
    await message.answer(get_text(lang, "help_text"))


@router.message(lambda m: m.text and m.text == "/cookies")
async def cookies_prompt(message: Message):
    lang = await get_user_language(message)
    await message.answer(
        "Отправь файл cookies.txt или скопируй его содержимое текстом.\n"
        "Можно задать cookies отдельно для платформы:\n"
        "/cookies_youtube\n/cookies_instagram\n/cookies_twitter\n/cookies_facebook"
    )


for _platform in ("youtube", "instagram", "twitter", "facebook"):
    async def _cookies_platform(message: Message, _platform=_platform):
        lang = await get_user_language(message)
        await message.answer(f"Отправь cookies для {_platform} файлом или текстом.")

    router.message(lambda m, p=_platform: m.text and m.text == f"/cookies_{p}")(_cookies_platform)


@router.message(lambda m: m.text and _looks_like_cookies(m.text or ""))
async def cookies_text(message: Message):
    try:
        platform = _detect_platform(message.text or "")
        dest = Path(settings.temp_dir) / f"user_{message.from_user.id}" / f"cookies_{platform}.txt"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(message.text, encoding="utf-8")
        if platform == "youtube":
            settings.youtube_cookies_file = str(dest)
        elif platform == "instagram":
            settings.instagram_cookies_file = str(dest)
        elif platform == "twitter":
            settings.twitter_cookies_file = str(dest)
        elif platform == "facebook":
            settings.facebook_cookies_file = str(dest)
        else:
            settings.cookies_path = str(dest)
        await message.answer(f"Cookies для {platform} сохранены и будут использоваться для загрузок.")
    except Exception:
        logger.exception("Cookies text save failed")
        await message.answer("Не удалось сохранить cookies из текста.")


@router.message(lambda m: m.document and m.document.file_name and "cookie" in m.document.file_name.lower())
async def cookies_upload(message: Message):
    lang = await get_user_language(message)
    try:
        file = await message.bot.get_file(message.document.file_id)
        dest = Path(settings.temp_dir) / f"user_{message.from_user.id}" / "cookies.txt"
        dest.parent.mkdir(parents=True, exist_ok=True)
        await message.bot.download_file(file.file_path, destination=str(dest))
        settings.cookies_path = str(dest)
        await message.answer("Cookies сохранены и будут использоваться для загрузок.")
    except Exception:
        logger.exception("Cookies upload failed")
        await message.answer("Не удалось сохранить cookies.")
