from typing import Optional, List
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from mediasave.app.database.models import User, Download, UserSetting, Platform, MediaType, DownloadStatus


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalar_one_or_none()

    async def get_or_create(self, telegram_id: int, username: str | None = None, first_name: str | None = None, last_name: str | None = None) -> User:
        user = await self.get_by_telegram_id(telegram_id)
        if not user:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                language="ru",
            )
            self.session.add(user)
            await self.session.flush()
        else:
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            user.last_seen = datetime.now(timezone.utc)
        return user

    async def set_language(self, user_id: int, language: str) -> None:
        user = await self.session.get(User, user_id)
        if user:
            user.language = language


class DownloadRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: int, url: str, platform: Platform, media_type: MediaType) -> Download:
        download = Download(
            user_id=user_id,
            url=url,
            platform=platform,
            media_type=media_type,
            status=DownloadStatus.PENDING,
        )
        self.session.add(download)
        await self.session.flush()
        return download

    async def get_by_id(self, download_id: int) -> Optional[Download]:
        return await self.session.get(Download, download_id)

    async def update_status(self, download_id: int, status: DownloadStatus, file_path: str | None = None, error_message: str | None = None) -> Optional[Download]:
        download = await self.get_by_id(download_id)
        if download:
            download.status = status
            if file_path:
                download.file_path = file_path
            if error_message:
                download.error_message = error_message
            download.updated_at = datetime.now(timezone.utc)
        return download

    async def get_user_history(self, user_id: int, limit: int = 20) -> List[Download]:
        result = await self.session.execute(
            select(Download).where(Download.user_id == user_id).order_by(desc(Download.created_at)).limit(limit)
        )
        return list(result.scalars().all())

    async def get_stats(self):
        users_count = (await self.session.execute(select(func.count(User.id)))).scalar_one()
        downloads_today = (await self.session.execute(
            select(func.count(Download.id)).where(Download.created_at >= datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0))
        )).scalar_one()
        errors_today = (await self.session.execute(
            select(func.count(Download.id)).where(
                Download.created_at >= datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0),
                Download.status == DownloadStatus.FAILED,
            )
        )).scalar_one()
        return users_count, downloads_today, errors_today


class UserSettingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, user_id: int, key: str) -> Optional[str]:
        result = await self.session.execute(select(UserSetting).where(UserSetting.user_id == user_id, UserSetting.key == key))
        setting = result.scalar_one_or_none()
        return setting.value if setting else None

    async def set(self, user_id: int, key: str, value: str) -> None:
        result = await self.session.execute(select(UserSetting).where(UserSetting.user_id == user_id, UserSetting.key == key))
        setting = result.scalar_one_or_none()
        if setting:
            setting.value = value
            setting.updated_at = datetime.now(timezone.utc)
        else:
            setting = UserSetting(user_id=user_id, key=key, value=value)
            self.session.add(setting)
