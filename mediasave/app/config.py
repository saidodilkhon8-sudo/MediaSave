import os
import shutil
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


ENV_FILE = Path(__file__).resolve().parents[1] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    bot_token: str = ""
    admin_ids: str = ""
    youtube_cookies_file: str = ""
    database_url: str = "sqlite+aiosqlite:///mediasave.db"
    temp_dir: str = "./temp"
    max_file_size_mb: int = 2000
    max_queue_size: int = 10
    download_timeout: int = 300
    ffmpeg_timeout: int = 120
    ffmpeg_path: str = "ffmpeg"
    log_level: str = "INFO"
    auto_delete_hours: int = 24
    default_language: str = "ru"

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
    def admin_ids_list(self) -> list[int]:
        if not self.admin_ids:
            return []
        return [int(x.strip()) for x in self.admin_ids.split(",") if x.strip()]


settings = Settings()
