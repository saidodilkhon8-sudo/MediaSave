from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from mediasave.app.database.models import User, UserSetting, Download


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalar_one_or_none()

    async def create(self, telegram_id: int, username: Optional[str] = None,
                     first_name: Optional[str] = None, last_name: Optional[str] = None) -> User:
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_or_create(self, telegram_id: int, username: Optional[str] = None,
                            first_name: Optional[str] = None, last_name: Optional[str] = None) -> User:
        user = await self.get_by_telegram_id(telegram_id)
        if not user:
            user = await self.create(telegram_id, username, first_name, last_name)
        return user

    async def set_language(self, user_id: int, language: str) -> None:
        user = await self.session.get(User, user_id)
        if user:
            user.language = language
            await self.session.commit()


class UserSettingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, user_id: int, key: str) -> Optional[str]:
        result = await self.session.execute(
            select(UserSetting.value).where(UserSetting.user_id == user_id, UserSetting.key == key)
        )
        return result.scalar_one_or_none()

    async def set(self, user_id: int, key: str, value: str) -> None:
        setting = await self.session.get(UserSetting, (user_id, key)) if hasattr(UserSetting, 'user_id') else None
        # Try to find existing
        result = await self.session.execute(
            select(UserSetting).where(UserSetting.user_id == user_id, UserSetting.key == key)
        )
        setting = result.scalar_one_or_none()
        if setting:
            setting.value = value
        else:
            setting = UserSetting(user_id=user_id, key=key, value=value)
            self.session.add(setting)
        await self.session.commit()


class DownloadRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: int, url: str, platform: str, media_type: str,
                     status: str = "pending", file_path: Optional[str] = None,
                     file_size: Optional[int] = None, duration: Optional[float] = None,
                     error_message: Optional[str] = None) -> Download:
        download = Download(
            user_id=user_id,
            url=url,
            platform=platform,
            media_type=media_type,
            status=status,
            file_path=file_path,
            file_size=file_size,
            duration=duration,
            error_message=error_message,
        )
        self.session.add(download)
        await self.session.commit()
        await self.session.refresh(download)
        return download

    async def update_status(self, download_id: int, status: str,
                            error_message: Optional[str] = None,
                            file_path: Optional[str] = None) -> None:
        download = await self.session.get(Download, download_id)
        if download:
            download.status = status
            if file_path is not None:
                download.file_path = file_path
            if error_message:
                download.error_message = error_message
            await self.session.commit()

    async def get_recent_by_user(self, user_id: int, limit: int = 20) -> list[Download]:
        result = await self.session.execute(
            select(Download)
            .where(Download.user_id == user_id)
            .order_by(Download.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
