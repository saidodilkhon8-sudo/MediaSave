import os
from pathlib import Path
from typing import Optional, Tuple
from mediasave.app.media.ffmpeg import run_ffmpeg


async def extract_audio(input_path: str, output_path: str, format: str = "mp3") -> Tuple[bool, Optional[str]]:
    ext = format.lower()
    output = str(Path(output_path).with_suffix(f".{ext}"))
    if ext == "mp3":
        success, error = await run_ffmpeg([
            "-i", input_path,
            "-vn",
            "-c:a", "libmp3lame",
            "-q:a", "2",
            output,
        ])
    else:
        success, error = await run_ffmpeg([
            "-i", input_path,
            "-vn",
            "-c:a", "aac",
            "-b:a", "192k",
            str(Path(output).with_suffix(".m4a")),
        ])
        output = str(Path(output).with_suffix(".m4a"))
    return success, error if not success else None
