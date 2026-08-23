import os
from pathlib import Path
from typing import Optional, Tuple
from mediasave.app.media.ffmpeg import run_ffmpeg, get_video_duration
from mediasave.app.media.audio import extract_audio
from mediasave.app.media.video_note import create_video_note
from mediasave.app.media.thumbnail import create_thumbnail, extract_existing_thumbnail
from mediasave.app.config import settings


class MediaService:
    def __init__(self, temp_dir: Path):
        self.temp_dir = temp_dir
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    async def create_circle(self, input_path: str) -> Tuple[Optional[str], Optional[str]]:
        output = str(self.temp_dir / f"circle_{Path(input_path).stem}.mp4")
        success, error = await create_video_note(input_path, output)
        return output if success else None, error

    async def create_mp3(self, input_path: str) -> Tuple[Optional[str], Optional[str]]:
        output = str(self.temp_dir / f"audio_{Path(input_path).stem}.mp3")
        success, error = await extract_audio(input_path, output)
        return output if success else None, error

    async def create_thumbnail(self, input_path: str) -> Tuple[Optional[str], Optional[str]]:
        output = str(self.temp_dir / f"thumb_{Path(input_path).stem}.jpg")
        success, error = await create_thumbnail(input_path, output)
        return output if success else None, error

    async def cut_video(self, input_path: str, start: float, end: float) -> Tuple[Optional[str], Optional[str]]:
        output = str(self.temp_dir / f"cut_{Path(input_path).stem}.mp4")
        success, error = await run_ffmpeg([
            "-i", input_path,
            "-ss", str(start),
            "-to", str(end),
            "-c", "copy",
            output,
        ])
        return output if success else None, error
