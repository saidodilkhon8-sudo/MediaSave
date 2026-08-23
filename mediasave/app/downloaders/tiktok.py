import re
from mediasave.app.downloaders.base import BaseDownloader
from mediasave.app.downloaders.schemas import MediaInfo, PlatformType, MediaType


class TikTokDownloader(BaseDownloader):
    def can_handle(self, url: str) -> bool:
        patterns = [
            r"(https?://)?(www\.)?tiktok\.com/",
            r"(https?://)?(www\.)?vm\.tiktok\.com/",
        ]
        return any(re.search(p, url) for p in patterns)

    async def get_info(self, url: str) -> MediaInfo:
        import yt_dlp
        ydl_opts = {"quiet": True, "no_warnings": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        return MediaInfo(
            url=url,
            platform=PlatformType.TIKTOK,
            media_type=MediaType.VIDEO,
            title=info.get("title") or info.get("description"),
            duration=info.get("duration"),
            file_size=info.get("filesize") or info.get("filesize_approx"),
            thumbnail_url=info.get("thumbnail"),
            uploader=info.get("uploader"),
        )

    async def download(self, url: str, output_dir: str, quality: str = "best") -> str:
        import yt_dlp
        import os
        ydl_opts = {
            "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)
