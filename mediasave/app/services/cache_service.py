"""
Кэширование скачанных файлов для избежания повторных загрузок
"""
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timezone, timedelta
from mediasave.app.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Управление кэшем скачанных файлов"""

    def __init__(self, cache_dir: Path = None):
        self.cache_dir = cache_dir or settings.temp_path / ".cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _url_hash(url: str) -> str:
        """Создать хеш URL для ключа кэша"""
        return hashlib.md5(url.encode()).hexdigest()

    def get_cache_path(self, url: str) -> Path:
        """Получить путь кэша для URL"""
        url_hash = self._url_hash(url)
        return self.cache_dir / url_hash

    def get_cached_file(self, url: str, max_age_hours: int = 72) -> Path | None:
        """Получить кэшированный файл, если он существует и свежий"""
        cache_path = self.get_cache_path(url)
        
        if not cache_path.exists():
            return None
        
        # Проверить возраст файла
        mtime = datetime.fromtimestamp(cache_path.stat().st_mtime, tz=timezone.utc)
        if datetime.now(timezone.utc) - mtime > timedelta(hours=max_age_hours):
            logger.info(f"Cache expired for {url[:50]}...")
            self._delete_cache(cache_path)
            return None
        
        logger.info(f"Cache hit for {url[:50]}...")
        return cache_path

    def save_to_cache(self, url: str, file_path: str | Path) -> bool:
        """Сохранить файл в кэш"""
        try:
            cache_path = self.get_cache_path(url)
            file_path = Path(file_path)
            
            if not file_path.exists():
                logger.warning(f"File not found for caching: {file_path}")
                return False
            
            # Создать символическую ссылку или скопировать
            if cache_path.exists():
                self._delete_cache(cache_path)
            
            cache_path.write_bytes(file_path.read_bytes())
            logger.info(f"Cached file: {url[:50]}... ({cache_path.stat().st_size / 1024 / 1024:.2f} MB)")
            return True
        except Exception as e:
            logger.error(f"Failed to cache file: {e}")
            return False

    def clear_old_cache(self, max_age_hours: int = 72) -> int:
        """Очистить старые файлы кэша"""
        count = 0
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
        
        for cache_file in self.cache_dir.glob("*"):
            if cache_file.is_file():
                mtime = datetime.fromtimestamp(cache_file.stat().st_mtime, tz=timezone.utc)
                if mtime < cutoff_time:
                    self._delete_cache(cache_file)
                    count += 1
        
        logger.info(f"Cleared {count} old cache files")
        return count

    @staticmethod
    def _delete_cache(path: Path) -> None:
        """Удалить файл кэша"""
        try:
            if path.is_file():
                path.unlink()
        except Exception as e:
            logger.error(f"Failed to delete cache: {e}")

    def get_cache_size(self) -> int:
        """Получить общий размер кэша в байтах"""
        total = 0
        for file in self.cache_dir.glob("*"):
            if file.is_file():
                total += file.stat().st_size
        return total

    def clear_all_cache(self) -> int:
        """Полностью очистить кэш"""
        count = 0
        for cache_file in self.cache_dir.glob("*"):
            if cache_file.is_file():
                self._delete_cache(cache_file)
                count += 1
        logger.info(f"Cleared all cache ({count} files)")
        return count
