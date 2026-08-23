from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from mediasave.app.database.database import get_session
from mediasave.app.database.repositories import UserRepository
from mediasave.app.i18n import get_text
from mediasave.app.config import settings

router = Router()


async def get_user_language(message: Message) -> str:
    async with get_session() as session:
        user = await UserRepository(session).get_by_telegram_id(message.from_user.id)
        return user.language if user else "ru"


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
    lang = "ru"
    text = get_text(lang, "start_message")
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text(lang, "menu_download"))],
            [KeyboardButton(text=get_text(lang, "menu_settings")), KeyboardButton(text=get_text(lang, "menu_history"))],
            [KeyboardButton(text=get_text(lang, "menu_help"))],
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
