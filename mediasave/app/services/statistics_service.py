"""
Сервис сбора и анализа статистики использования
"""
import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, func
from mediasave.app.database.database import get_session
from mediasave.app.database.models import User, Download, DownloadStatus, Platform

logger = logging.getLogger(__name__)


class StatisticsService:
    """Сбор и анализ статистики использования"""

    @staticmethod
    async def get_user_stats(user_id: int) -> dict:
        """Получить статистику конкретного пользователя"""
        async with get_session() as session:
            user = await session.get(User, {"telegram_id": user_id})
            if not user:
                return {}
            
            total_downloads = await session.scalar(
                select(func.count(Download.id)).where(Download.user_id == user.id)
            ) or 0
            
            successful = await session.scalar(
                select(func.count(Download.id)).where(
                    (Download.user_id == user.id) & (Download.status == DownloadStatus.COMPLETED)
                )
            ) or 0
            
            total_size = await session.scalar(
                select(func.sum(Download.file_size)).where(Download.user_id == user.id)
            ) or 0
            
            return {
                "total_downloads": total_downloads,
                "successful": successful,
                "failed": total_downloads - successful,
                "total_size_mb": total_size / 1024 / 1024,
                "success_rate": (successful / total_downloads * 100) if total_downloads > 0 else 0
            }

    @staticmethod
    async def get_platform_stats() -> dict:
        """Получить статистику по платформам"""
        async with get_session() as session:
            stats = {}
            for platform in Platform:
                total = await session.scalar(
                    select(func.count(Download.id)).where(Download.platform == platform)
                ) or 0
                
                if total == 0:
                    continue
                
                successful = await session.scalar(
                    select(func.count(Download.id)).where(
                        (Download.platform == platform) & (Download.status == DownloadStatus.COMPLETED)
                    )
                ) or 0
                
                stats[platform.value] = {
                    "total": total,
                    "successful": successful,
                    "failed": total - successful,
                    "success_rate": (successful / total * 100) if total > 0 else 0
                }
            
            return stats

    @staticmethod
    async def get_daily_stats(days: int = 30) -> dict:
        """Получить ежедневную статистику за N дней"""
        async with get_session() as session:
            stats = {}
            
            for i in range(days):
                date = (datetime.now(timezone.utc) - timedelta(days=i)).date()
                
                count = await session.scalar(
                    select(func.count(Download.id)).where(
                        func.date(Download.created_at) == date
                    )
                ) or 0
                
                if count > 0:
                    stats[str(date)] = count
            
            return dict(sorted(stats.items()))

    @staticmethod
    async def get_top_users(limit: int = 10) -> list:
        """Получить топ пользователей по загрузкам"""
        async with get_session() as session:
            result = await session.execute(
                select(User.telegram_id, func.count(Download.id).label("downloads"))
                .join(Download)
                .group_by(User.id)
                .order_by(func.count(Download.id).desc())
                .limit(limit)
            )
            
            rows = result.all()
            return [{"user_id": r[0], "downloads": r[1]} for r in rows]

    @staticmethod
    async def get_error_stats() -> dict:
        """Получить статистику ошибок"""
        async with get_session() as session:
            total_errors = await session.scalar(
                select(func.count(Download.id)).where(Download.status == DownloadStatus.FAILED)
            ) or 0
            
            by_platform = {}
            for platform in Platform:
                count = await session.scalar(
                    select(func.count(Download.id)).where(
                        (Download.platform == platform) & (Download.status == DownloadStatus.FAILED)
                    )
                ) or 0
                if count > 0:
                    by_platform[platform.value] = count
            
            return {
                "total": total_errors,
                "by_platform": by_platform
            }

    @staticmethod
    async def cleanup_old_downloads(days: int = 30) -> int:
        """Удалить старые записи загрузок (старше N дней)"""
        from sqlalchemy import delete
        
        async with get_session() as session:
            cutoff = datetime.now(timezone.utc) - timedelta(days=days)
            
            stmt = delete(Download).where(Download.created_at < cutoff)
            result = await session.execute(stmt)
            await session.commit()
            
            logger.info(f"Cleaned up {result.rowcount} old download records")
            return result.rowcount
