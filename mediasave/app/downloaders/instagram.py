import re
import os
import logging
from typing import List, Union
from mediasave.app.downloaders.base import BaseDownloader
from mediasave.app.downloaders.schemas import MediaInfo, PlatformType, MediaType
from mediasave.app.downloaders.utils import build_ytdlp_opts

logger = logging.getLogger(__name__)


class InstagramDownloader(BaseDownloader):
    def can_handle(self, url: str) -> bool:
        patterns = [
            r"(https?://)?(www\.)?instagram\.com/",
            r"(https?://)?(www\.)?instagr\.am/",
        ]
        return any(re.search(p, url) for p in patterns)

    async def get_info(self, url: str) -> MediaInfo:
        import yt_dlp
        ydl_opts = build_ytdlp_opts(url)
        logger.info("Instagram get_info: %s", url)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        entries = []
        if info.get("_type") == "playlist" and info.get("entries"):
            for entry in info["entries"]:
                entries.append(MediaInfo(
                    url=entry.get("url", url),
                    platform=PlatformType.INSTAGRAM,
                    media_type=MediaType.VIDEO if entry.get("vcodec") != "none" else MediaType.IMAGE,
                    title=entry.get("title") or entry.get("description"),
                    duration=entry.get("duration"),
                    file_size=entry.get("filesize") or entry.get("filesize_approx"),
                    thumbnail_url=entry.get("thumbnail"),
                    uploader=entry.get("uploader"),
                ))
            return MediaInfo(
                url=url,
                platform=PlatformType.INSTAGRAM,
                media_type=MediaType.CAROUSEL,
                title=info.get("title") or info.get("description"),
                duration=info.get("duration"),
                file_size=info.get("filesize") or info.get("filesize_approx"),
                thumbnail_url=info.get("thumbnail"),
                uploader=info.get("uploader"),
                entries=entries,
            )

        media_type = MediaType.VIDEO if info.get("vcodec") != "none" else MediaType.IMAGE
        return MediaInfo(
            url=url,
            platform=PlatformType.INSTAGRAM,
            media_type=media_type,
            title=info.get("title") or info.get("description"),
            duration=info.get("duration"),
            file_size=info.get("filesize") or info.get("filesize_approx"),
            thumbnail_url=info.get("thumbnail"),
            uploader=info.get("uploader"),
        )

    async def download(self, url: str, output_dir: str, quality: str = "best") -> Union[str, List[str]]:
        import yt_dlp
        ydl_opts = build_ytdlp_opts(url, {"outtmpl": os.path.join(output_dir, "%(title)s_%(playlist_index)02d.%(ext)s")})
        logger.info("Instagram download: %s -> %s", url, output_dir)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        if info.get("_type") == "playlist" and info.get("entries"):
            files: List[str] = []
            for entry in info["entries"]:
                if entry:
                    requested = entry.get("requested_downloads", [{}])[0] if entry.get("requested_downloads") else {}
                    filepath = requested.get("filepath") or requested.get("filename") or ydl.prepare_filename(entry)
                    if filepath and os.path.isfile(filepath):
                        files.append(filepath)
            if files:
                return files
            return [ydl.prepare_filename(info)]

        requested = info.get("requested_downloads", [{}])[0] if info.get("requested_downloads") else {}
        filepath = requested.get("filepath") or requested.get("filename") or ydl.prepare_filename(info)
        if filepath and os.path.isfile(filepath):
            return filepath
        return ydl.prepare_filename(info)
