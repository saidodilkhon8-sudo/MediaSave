import asyncio
import logging
from pathlib import Path
from typing import Optional, List, Dict
import yt_dlp
from mediasave.app.config import settings
from mediasave.app.downloaders.youtube import YouTubeDownloader
from mediasave.app.services.download_service import DownloadService

logger = logging.getLogger(__name__)


class MusicSearchService:
    def __init__(self) -> None:
        self.downloader = YouTubeDownloader()

    async def search(self, query: str) -> Optional[List[Dict]]:
        search_url = f"ytsearch10:{query}"
        temp_dir = settings.temp_path / "music_search"
        temp_dir.mkdir(parents=True, exist_ok=True)
        try:
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "ffmpeg_location": settings.ffmpeg_executable,
                "extract_flat": "in_playlist",
            }
            cookie_path = settings.effective_cookies_path
            if cookie_path:
                ydl_opts["cookiefile"] = cookie_path
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                meta = ydl.extract_info(search_url, download=False)
                if not meta or not meta.get("entries"):
                    return None
                results = []
                for entry in meta["entries"]:
                    url = entry.get("url") or entry.get("webpage_url")
                    if not url:
                        continue
                    results.append({
                        "url": url,
                        "title": entry.get("title"),
                        "uploader": entry.get("uploader") or entry.get("channel"),
                        "duration": entry.get("duration"),
                        "thumbnail": (entry.get("thumbnails") or [{}])[-1].get("url") if entry.get("thumbnails") else None,
                    })
                return results or None
        except Exception:
            logger.exception("Music search failed")
            return None

    async def download_track(self, url: str) -> Optional[dict]:
        temp_dir = settings.temp_path / "music_search"
        temp_dir.mkdir(parents=True, exist_ok=True)
        service = DownloadService(self.downloader, temp_dir)
        try:
            file_path, info = await service.process(url, quality="best")
            if not file_path or not Path(file_path).is_file():
                return None
            return {
                "path": str(file_path),
                "title": info.title if info else None,
                "uploader": info.uploader if info else None,
                "duration": info.duration if info else None,
            }
        except Exception:
            logger.exception("Music track download failed")
            return None
