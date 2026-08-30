import re
import logging
from typing import List, Union
from mediasave.app.downloaders.base import BaseDownloader
from mediasave.app.downloaders.schemas import MediaInfo, PlatformType, MediaType
from mediasave.app.downloaders.utils import build_ytdlp_opts

logger = logging.getLogger(__name__)


class PinterestDownloader(BaseDownloader):
    def can_handle(self, url: str) -> bool:
        patterns = [
            r"(https?://)?(www\.)?pinterest\.com/",
            r"(https?://)?(www\.)?pin\.it/",
        ]
        return any(re.search(p, url) for p in patterns)

    async def get_info(self, url: str) -> MediaInfo:
        import yt_dlp
        ydl_opts = build_ytdlp_opts(url)
        logger.info("Pinterest get_info: %s", url)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        return MediaInfo(
            url=url,
            platform=PlatformType.PINTEREST,
            media_type=MediaType.VIDEO if info.get("vcodec") != "none" else MediaType.IMAGE,
            title=info.get("title") or info.get("description"),
            duration=info.get("duration"),
            file_size=info.get("filesize") or info.get("filesize_approx"),
            thumbnail_url=info.get("thumbnail"),
            uploader=info.get("uploader"),
        )

    async def download(self, url: str, output_dir: str, quality: str = "best") -> Union[str, List[str]]:
        import yt_dlp, os
        ydl_opts = build_ytdlp_opts(url, {"outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s")})
        logger.info("Pinterest download: %s -> %s", url, output_dir)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)
