import os
import asyncio
import uuid
import logging
from pathlib import Path
from typing import Optional, Callable, Union, List
from mediasave.app.downloaders.schemas import MediaInfo
from mediasave.app.downloaders.base import BaseDownloader
from mediasave.app.media.ffmpeg import run_ffmpeg
from mediasave.app.config import settings
from mediasave.app.services.retry import retry_async
from mediasave.app.downloaders.utils import set_progress_callback, reset_progress_callback


logger = logging.getLogger(__name__)


_semaphore = asyncio.Semaphore(settings.download_concurrency)


class DownloadService:
    def __init__(self, downloader: BaseDownloader, temp_dir: Path):
        self.downloader = downloader
        self.temp_dir = temp_dir
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    async def process(self, url: str, on_progress: Optional[Callable[[int], None]] = None, quality: str = "best") -> tuple[Optional[Union[str, List[str]]], Optional[MediaInfo]]:
        task_id = str(uuid.uuid4())
        task_dir = self.temp_dir / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        throttled = self._throttle(on_progress) if on_progress else None
        loop = asyncio.get_running_loop()

        def progress_hook(data):
            if not throttled or data.get("status") != "downloading":
                return
            total = data.get("total_bytes") or data.get("total_bytes_estimate") or 0
            downloaded = data.get("downloaded_bytes") or 0
            speed = data.get("speed") or 0
            pct = int(downloaded * 100 / total) if total else 0
            loop.call_soon_threadsafe(asyncio.create_task, throttled(pct, speed, total))

        progress_token = set_progress_callback(progress_hook)
        try:
            logger.info("DownloadService.get_info start: url=%s, quality=%s", url, quality)
            try:
                info = await retry_async(lambda: self.downloader.get_info(url), max_attempts=3, delay=2, backoff=2)
            except Exception as e:
                error_msg = str(e).lower()
                logger.error("Failed to get video info: %s", e)
                if "private" in error_msg or "age" in error_msg:
                    raise RuntimeError("Это видео защищено от скачивания или требует авторизацию")
                elif "unavailable" in error_msg or "removed" in error_msg:
                    raise RuntimeError("Видео недоступно или было удалено")
                elif "403" in error_msg:
                    raise RuntimeError("Доступ запрещен. Может потребоваться авторизация.")
                elif "geoblocked" in error_msg or "not available" in error_msg:
                    raise RuntimeError("Видео недоступно в вашем регионе")
                raise
            
            logger.info("DownloadService.get_info done: platform=%s, title=%s", info.platform if info else None, info.title if info else None)
            async with _semaphore:
                logger.info("DownloadService.download start: url=%s, quality=%s", url, quality)
                try:
                    file_path = await retry_async(lambda: self.downloader.download(url, str(task_dir), quality=quality), max_attempts=3, delay=2, backoff=2)
                except Exception as e:
                    logger.error("Download failed: %s", e)
                    raise
                logger.info("DownloadService.download done: file_path=%s", file_path)
            if throttled:
                await throttled(100)
            if isinstance(file_path, list):
                valid = [p for p in file_path if Path(p).is_file() and Path(p).stat().st_size > 1024]
                return valid if valid else None, info
            if file_path and Path(file_path).is_file() and Path(file_path).stat().st_size > 1024:
                return file_path, info
            return None, info
        except Exception as e:
            if task_dir.exists():
                import shutil
                shutil.rmtree(task_dir, ignore_errors=True)
            logger.error("DownloadService failed: url=%s, error=%s", url, e)
            raise e
        finally:
            reset_progress_callback(progress_token)

    def _throttle(self, on_progress: Optional[Callable[[int], None]]) -> Callable[[int], None]:
        last_update = 0.0

        async def wrapped(pct: int, speed: float = 0, total: int = 0) -> None:
            nonlocal last_update
            now = asyncio.get_event_loop().time()
            if now - last_update >= 1.0:
                last_update = now
                if on_progress:
                    await on_progress(pct, speed, total)

        return wrapped
