from pathlib import Path
from mediasave.app.media.ffmpeg import run_ffmpeg


async def cut_video(input_path: str, start: str, end: str, output_path: str) -> tuple[bool, str]:
    success, error = await run_ffmpeg([
        "-ss", start,
        "-to", end,
        "-i", input_path,
        "-c", "copy",
        output_path,
    ])
    if not success and Path(output_path).exists():
        Path(output_path).unlink(missing_ok=True)
    return success, error
