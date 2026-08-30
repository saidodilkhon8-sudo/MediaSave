from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select, func
from mediasave.app.config import settings
from mediasave.app.database.database import get_session
from mediasave.app.database.models import User, Download, DownloadStatus

router = Router()


def _is_admin(user_id: int) -> bool:
    return user_id in settings.admin_ids_list


def _keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Users", callback_data="admin:users")],
        [InlineKeyboardButton(text="Downloads", callback_data="admin:downloads")],
        [InlineKeyboardButton(text="Errors", callback_data="admin:errors")],
        [InlineKeyboardButton(text="Statistics", callback_data="admin:stats")],
    ])


async def _stats_text() -> str:
    async with get_session() as session:
        users = await session.scalar(select(func.count(User.id))) or 0
        downloads = await session.scalar(select(func.count(Download.id))) or 0
        completed = await session.scalar(
            select(func.count(Download.id)).where(Download.status == DownloadStatus.COMPLETED)
        ) or 0
        errors = await session.scalar(
            select(func.count(Download.id)).where(Download.status == DownloadStatus.FAILED)
        ) or 0
    return f"MediaSave\n\nUsers: {users}\nDownloads: {downloads}\nCompleted: {completed}\nErrors: {errors}"


@router.message(F.text == "/admin")
async def admin_menu(message: Message):
    if _is_admin(message.from_user.id):
        await message.answer(await _stats_text(), reply_markup=_keyboard())


@router.callback_query(F.data.startswith("admin:"))
async def admin_action(callback: CallbackQuery):
    if not _is_admin(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return
    action = callback.data.split(":", 1)[1]
    async with get_session() as session:
        if action == "users":
            value = await session.scalar(select(func.count(User.id))) or 0
            text = f"Users: {value}"
        elif action == "downloads":
            value = await session.scalar(select(func.count(Download.id))) or 0
            text = f"Downloads: {value}"
        elif action == "errors":
            value = await session.scalar(select(func.count(Download.id)).where(Download.status == DownloadStatus.FAILED)) or 0
            text = f"Errors: {value}"
        else:
            text = await _stats_text()
    await callback.message.edit_text(text, reply_markup=_keyboard())
    await callback.answer()
