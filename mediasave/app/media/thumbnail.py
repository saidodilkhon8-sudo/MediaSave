import os
from pathlib import Path
from typing import Optional, Tuple
from mediasave.app.media.ffmpeg import run_ffmpeg, get_video_duration


async def create_thumbnail(input_path: str, output_path: str, time_offset: float = 1.0) -> Tuple[bool, Optional[str]]:
    success, error = await run_ffmpeg([
        "-i", input_path,
        "-ss", str(time_offset),
        "-vframes", "1",
        "-vf", "scale=320:-1",
        output_path,
    ])
    return success, error if not success else None


async def extract_existing_thumbnail(input_path: str, output_path: str) -> bool:
    success, _ = await run_ffmpeg([
        "-i", input_path,
        "-an",
        "-vcodec", "copy",
        "-map", "0:v",
        "-f", "mjpeg",
        output_path,
    ])
    return success
