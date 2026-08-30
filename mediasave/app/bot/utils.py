from typing import Optional
from aiogram.types import Message
from mediasave.app.database.database import get_session
from mediasave.app.database.repositories import UserRepository


async def get_user_language(message: Message) -> str:
    async with get_session() as session:
        user = await UserRepository(session).get_by_telegram_id(message.from_user.id)
        return user.language if user else "ru"
