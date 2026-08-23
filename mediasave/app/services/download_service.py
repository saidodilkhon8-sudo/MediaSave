import os
import asyncio
import uuid
from pathlib import Path
from typing import Optional
from mediasave.app.downloaders.schemas import MediaInfo
from mediasave.app.downloaders.base import BaseDownloader
from mediasave.app.media.ffmpeg import run_ffmpeg
from mediasave.app.config import settings


class DownloadService:
    def __init__(self, downloader: BaseDownloader, temp_dir: Path):
        self.downloader = downloader
        self.temp_dir = temp_dir
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    async def process(self, url: str, on_progress=None, quality: str = "best") -> tuple[Optional[str], Optional[MediaInfo]]:
        task_id = str(uuid.uuid4())
        task_dir = self.temp_dir / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        try:
            info = await self.downloader.get_info(url)
            file_path = await self.downloader.download(url, str(task_dir), quality=quality)
            if on_progress:
                await on_progress(100)
            return file_path, info
        except Exception as e:
            if task_dir.exists():
                import shutil
                shutil.rmtree(task_dir, ignore_errors=True)
            raise e
