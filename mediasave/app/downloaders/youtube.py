import re
import logging
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from mediasave.app.downloaders.base import BaseDownloader
from mediasave.app.downloaders.schemas import MediaInfo, PlatformType, MediaType
from mediasave.app.downloaders.utils import build_ytdlp_opts
from mediasave.app.config import settings

logger = logging.getLogger(__name__)


class YouTubeDownloader(BaseDownloader):
    def can_handle(self, url: str) -> bool:
        patterns = [
            r"(https?://)?(www\.)?youtube\.com/watch\?v=",
            r"(https?://)?youtu\.be/",
            r"(https?://)?(www\.)?youtube\.com/shorts/",
        ]
        return any(re.search(p, url) for p in patterns)

    async def get_info(self, url: str) -> MediaInfo:
        import yt_dlp
        last_error = None
        for client in ("android_vr", "android", "ios", "web", "mweb", "mediaconnect"):
            try:
                ydl_opts = {
                    "quiet": True,
                    "no_warnings": True,
                    "ffmpeg_location": settings.ffmpeg_executable,
                    "extractor_args": {"youtube": {"player_client": [client]}},
                    "http_headers": {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Accept-Language": "en-US,en;q=0.5",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Connection": "keep-alive",
                        "Upgrade-Insecure-Requests": "1",
                    },
                    "proxy": settings.proxy_url or None,
                    "timeout": settings.download_timeout,
                    "retries": 5,
                    "fragment_retries": 5,
                    "skip_unavailable_fragments": True,
                }
                cookie_path = settings.platform_cookies_path("youtube")
                if cookie_path:
                    ydl_opts["cookiefile"] = cookie_path
                else:
                    logger.warning("YouTube download: no cookies configured")
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                break
            except yt_dlp.utils.DownloadError as error:
                last_error = error
                continue
        else:
            if last_error:
                raise last_error
            raise RuntimeError("YouTube: unsupported URL")

        is_short = "/shorts/" in url or info.get("duration", 0) <= 60
        platform = PlatformType.YOUTUBE_SHORTS if is_short else PlatformType.YOUTUBE
        media_type = MediaType.VIDEO if info.get("vcodec") != "none" else MediaType.AUDIO
        return MediaInfo(
            url=url,
            platform=platform,
            media_type=media_type,
            title=info.get("title"),
            duration=info.get("duration"),
            file_size=info.get("filesize") or info.get("filesize_approx"),
            thumbnail_url=info.get("thumbnail"),
            uploader=info.get("uploader"),
        )

    async def download(self, url: str, output_dir: str, quality: str = "best") -> str:
        import yt_dlp
        import os
        last_error = None
        for client in ("android_vr", "android", "ios", "web", "mweb", "mediaconnect"):
            try:
                ydl_opts = {
                    "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
                    "quiet": True,
                    "no_warnings": True,
                    "format": self._format_for_quality(quality),
                    "ffmpeg_location": settings.ffmpeg_executable,
                    "extractor_args": {"youtube": {"player_client": [client]}},
                    "http_headers": {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Accept-Language": "en-US,en;q=0.5",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Connection": "keep-alive",
                        "Upgrade-Insecure-Requests": "1",
                    },
                    "proxy": settings.proxy_url or None,
                    "timeout": settings.download_timeout,
                    "retries": 5,
                    "fragment_retries": 5,
                    "skip_unavailable_fragments": True,
                }
                cookie_path = settings.platform_cookies_path("youtube")
                if cookie_path:
                    ydl_opts["cookiefile"] = cookie_path
                else:
                    logger.warning("YouTube download: no cookies configured")
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
                    if os.path.isfile(filename):
                        return filename
                    for entry in info.get("entries", []):
                        if entry:
                            fn = ydl.prepare_filename(entry)
                            if os.path.isfile(fn):
                                return fn
                    return filename
            except yt_dlp.utils.DownloadError as error:
                last_error = error
                continue
        if last_error:
            raise last_error
        raise RuntimeError("YouTube: download failed")

    @staticmethod
    def _format_for_quality(quality: str) -> str:
        if quality == "best":
            return "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best[ext=mp4]/best"
        return (
            f"bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/"
            f"bestvideo[height<={quality}]+bestaudio/"
            f"best[height<={quality}][ext=mp4]/"
            f"best[height<={quality}]/best"
        )
