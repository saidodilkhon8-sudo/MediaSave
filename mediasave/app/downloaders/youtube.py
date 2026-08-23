import re
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from mediasave.app.downloaders.base import BaseDownloader
from mediasave.app.downloaders.schemas import MediaInfo, PlatformType, MediaType
from mediasave.app.config import settings
from mediasave.app.media.ffmpeg import run_ffmpeg


class YouTubeDownloader(BaseDownloader):
    def _ydl_options(self, **options):
        if settings.youtube_cookies_path:
            options["cookiefile"] = settings.youtube_cookies_path
        options["ffmpeg_location"] = settings.ffmpeg_executable
        options["extractor_args"] = {
            "youtube": {"player_client": ["android"]}
        }
        return options

    def can_handle(self, url: str) -> bool:
        patterns = [
            r"(https?://)?(www\.)?youtube\.com/watch\?v=",
            r"(https?://)?youtu\.be/",
            r"(https?://)?(www\.)?youtube\.com/shorts/",
        ]
        return any(re.search(p, url) for p in patterns)

    async def get_info(self, url: str) -> MediaInfo:
        import yt_dlp
        ydl_opts = self._ydl_options(quiet=True, no_warnings=True)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
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
        ydl_opts = self._ydl_options(
            outtmpl=os.path.join(output_dir, "%(title)s.%(ext)s"),
            quiet=True,
            no_warnings=True,
            format=self._format_for_quality(quality),
        )
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            for requested in info.get("requested_downloads", []):
                file_path = requested.get("filepath") or requested.get("filename")
                if file_path and Path(file_path).is_file():
                    return await self._convert_webm(file_path)

            downloaded_files = [
                path for path in Path(output_dir).iterdir()
                if path.is_file() and not path.name.endswith(".part")
            ]
            if downloaded_files:
                return await self._convert_webm(str(downloaded_files[0]))
            return await self._convert_webm(ydl.prepare_filename(info))

    @staticmethod
    def _format_for_quality(quality: str) -> str:
        if quality == "best":
            return "bestvideo*+bestaudio/best"
        return f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]"

    async def _convert_webm(self, file_path: str) -> str:
        source = Path(file_path)
        if source.suffix.lower() != ".webm" or not source.is_file():
            return file_path

        target = source.with_suffix(".mp4")
        success, _ = await run_ffmpeg([
            "-i", str(source),
            "-c:v", "libx264",
            "-c:a", "aac",
            "-movflags", "+faststart",
            str(target),
        ])
        if success and target.is_file():
            source.unlink(missing_ok=True)
            return str(target)
        return file_path
