import asyncio
import shutil
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from mediasave.app.config import settings

logger = logging.getLogger(__name__)


async def cleanup_temp_files():
    """Периодическая очистка старых файлов"""
    while True:
        try:
            cutoff = datetime.now(timezone.utc) - timedelta(hours=settings.auto_delete_hours)
            stats = {"deleted": 0, "size_freed_mb": 0}
            
            for user_dir in settings.temp_path.iterdir():
                if user_dir.is_dir() and user_dir.name.startswith("user_"):
                    for item in user_dir.iterdir():
                        if item.stat().st_mtime < cutoff.timestamp():
                            try:
                                if item.is_dir():
                                    size = sum(f.stat().st_size for f in item.rglob("*") if f.is_file())
                                    shutil.rmtree(item, ignore_errors=True)
                                    stats["deleted"] += 1
                                    stats["size_freed_mb"] += size / 1024 / 1024
                                else:
                                    stats["size_freed_mb"] += item.stat().st_size / 1024 / 1024
                                    item.unlink(missing_ok=True)
                                    stats["deleted"] += 1
                            except Exception as e:
                                logger.warning(f"Failed to delete {item}: {e}")
            
            if stats["deleted"] > 0:
                logger.info(f"Cleanup: deleted {stats['deleted']} items, freed {stats['size_freed_mb']:.2f} MB")
        
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
        
        await asyncio.sleep(settings.auto_delete_hours * 3600)


class CleanupService:
    """Утилиты очистки временных файлов"""

    @staticmethod
    async def get_temp_dir_size() -> int:
        """Получить размер временной директории в байтах"""
        total = 0
        try:
            if settings.temp_path.exists():
                for path in settings.temp_path.glob("**/*"):
                    if path.is_file():
                        total += path.stat().st_size
        except Exception as e:
            logger.error(f"Error calculating size: {e}")
        return total

    @staticmethod
    async def clear_incomplete_downloads() -> int:
        """Очистить незавершенные загрузки (.part файлы)"""
        count = 0
        try:
            if settings.temp_path.exists():
                for part_file in settings.temp_path.glob("**/*.part"):
                    part_file.unlink(missing_ok=True)
                    count += 1
        except Exception as e:
            logger.error(f"Error clearing incomplete: {e}")
        return count

    @staticmethod
    async def get_user_temp_size(user_id: int) -> int:
        """Получить размер файлов конкретного пользователя"""
        total = 0
        user_dir = settings.temp_path / f"user_{user_id}"
        try:
            if user_dir.exists():
                for path in user_dir.glob("**/*"):
                    if path.is_file():
                        total += path.stat().st_size
        except Exception as e:
            logger.error(f"Error calculating user size: {e}")
        return total
