import re
import logging
from mediasave.app.downloaders.base import BaseDownloader
from mediasave.app.downloaders.schemas import MediaInfo, PlatformType, MediaType
from mediasave.app.downloaders.utils import build_ytdlp_opts

logger = logging.getLogger(__name__)


class SnapchatDownloader(BaseDownloader):
    def can_handle(self, url: str) -> bool:
        patterns = [
            r"(https?://)?(www\.)?snapchat\.com/",
            r"(https?://)?(www\.)?snap\.chat/",
        ]
        return any(re.search(p, url) for p in patterns)

    async def get_info(self, url: str) -> MediaInfo:
        import yt_dlp
        ydl_opts = build_ytdlp_opts(url)
        logger.info("Snapchat get_info: %s", url)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        media_type = MediaType.VIDEO if info.get("vcodec") != "none" else MediaType.IMAGE
        return MediaInfo(
            url=url,
            platform=PlatformType.SNAPCHAT,
            media_type=media_type,
            title=info.get("title") or info.get("description"),
            duration=info.get("duration"),
            file_size=info.get("filesize") or info.get("filesize_approx"),
            thumbnail_url=info.get("thumbnail"),
            uploader=info.get("uploader"),
        )

    async def download(self, url: str, output_dir: str, quality: str = "best") -> str:
        import yt_dlp
        import os
        ydl_opts = build_ytdlp_opts(url, {"outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s")})
        logger.info("Snapchat download: %s -> %s", url, output_dir)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)
