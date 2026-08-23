import os
from pathlib import Path
from typing import Optional, Tuple
from mediasave.app.media.ffmpeg import run_ffmpeg, get_video_duration
from mediasave.app.config import settings


async def create_video_note(input_path: str, output_path: str, max_duration: float = 60.0) -> Tuple[bool, Optional[str]]:
    duration = get_video_duration(input_path)
    if duration and duration > max_duration:
        input_path = await trim_video(input_path, 0, max_duration)
    success, error = await run_ffmpeg([
        "-i", input_path,
        "-vf", "scale=640:640:force_original_aspect_ratio=decrease,pad=640:640:(ow-iw)/2:(oh-ih)/2",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        "-ar", "44100",
        "-ac", "1",
        "-movflags", "+faststart",
        "-t", str(max_duration),
        output_path,
    ])
    return success, error if not success else None


async def trim_video(input_path: str, start: float, end: float) -> str:
    output_path = str(Path(input_path).with_suffix(".trimmed.mp4"))
    success, error = await run_ffmpeg([
        "-i", input_path,
        "-ss", str(start),
        "-to", str(end),
        "-c", "copy",
        output_path,
    ])
    if not success:
        raise RuntimeError(f"Trim failed: {error}")
    return output_path
