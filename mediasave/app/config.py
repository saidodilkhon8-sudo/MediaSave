import os
import shutil
import base64
import tempfile
import warnings
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


ENV_FILE = Path(__file__).resolve().parents[1] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    bot_token: str = ""
    admin_ids: str = ""
    database_url: str = "sqlite+aiosqlite:///mediasave.db"
    temp_dir: str = "./temp"
    max_file_size_mb: int = 2000
    max_video_duration: int = 900
    download_concurrency: int = 3
    log_level: str = "INFO"
    auto_delete_hours: int = 24
    default_language: str = "ru"
    rate_limit_per_minute: int = 30
    ffmpeg_timeout: int = 120
    ffmpeg_path: str = "ffmpeg"
    download_timeout: int = 300
    music_api_key: str = ""
    lyrics_api_key: str = ""
    proxy_url: str = ""
    youtube_cookies_file: str = ""
    youtube_cookies_base64: str = ""
    cookies_path: str = ""
    instagram_cookies_file: str = ""
    instagram_cookies_base64: str = ""
    twitter_cookies_file: str = ""
    twitter_cookies_base64: str = ""
    facebook_cookies_file: str = ""
    facebook_cookies_base64: str = ""

    @property
    def temp_path(self) -> Path:
        return Path(self.temp_dir)

    @property
    def ffmpeg_executable(self) -> str:
        if self.ffmpeg_path != "ffmpeg" or shutil.which(self.ffmpeg_path):
            return self.ffmpeg_path
        try:
            import imageio_ffmpeg
            return imageio_ffmpeg.get_ffmpeg_exe()
        except ImportError:
            return self.ffmpeg_path

    @property
    def admin_ids_list(self) -> list:
        if not self.admin_ids:
            return []
        result = []
        for x in self.admin_ids.split(","):
            x = x.strip()
            if not x:
                continue
            if x.lstrip("-").isdigit():
                result.append(int(x))
            else:
                result.append(x)
        return result

    @property
    def effective_cookies_path(self) -> str:
        if self.cookies_path and Path(self.cookies_path).exists():
            return self.cookies_path
        return ""

    def platform_cookies_path(self, platform: str) -> str:
        platform = platform.lower()
        if platform == "youtube":
            if self.youtube_cookies_file and Path(self.youtube_cookies_file).exists():
                return self.youtube_cookies_file
            if self.youtube_cookies_base64:
                path = Path(tempfile.gettempdir()) / "mediasave-youtube-cookies.txt"
                if not path.exists():
                    path.write_bytes(base64.b64decode(self.youtube_cookies_base64))
                return str(path)
        if platform == "instagram":
            if self.instagram_cookies_file and Path(self.instagram_cookies_file).exists():
                return self.instagram_cookies_file
            if self.instagram_cookies_base64:
                path = Path(tempfile.gettempdir()) / "mediasave-instagram-cookies.txt"
                if not path.exists():
                    path.write_bytes(base64.b64decode(self.instagram_cookies_base64))
                return str(path)
        if platform == "twitter":
            if self.twitter_cookies_file and Path(self.twitter_cookies_file).exists():
                return self.twitter_cookies_file
            if self.twitter_cookies_base64:
                path = Path(tempfile.gettempdir()) / "mediasave-twitter-cookies.txt"
                if not path.exists():
                    path.write_bytes(base64.b64decode(self.twitter_cookies_base64))
                return str(path)
        if platform == "facebook":
            if self.facebook_cookies_file and Path(self.facebook_cookies_file).exists():
                return self.facebook_cookies_file
            if self.facebook_cookies_base64:
                path = Path(tempfile.gettempdir()) / "mediasave-facebook-cookies.txt"
                if not path.exists():
                    path.write_bytes(base64.b64decode(self.facebook_cookies_base64))
                return str(path)
        return self.effective_cookies_path


settings = Settings()

try:
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Couldn't find ffmpeg or avconv.*", category=RuntimeWarning)
        import pydub
    pydub.AudioSegment.converter = settings.ffmpeg_executable
    pydub.AudioSegment.ffmpeg = settings.ffmpeg_executable
except Exception:
    pass
