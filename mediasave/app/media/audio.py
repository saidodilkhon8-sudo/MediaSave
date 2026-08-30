from pathlib import Path
from mediasave.app.media.ffmpeg import run_ffmpeg


async def extract_audio(input_path: str, output_path: str) -> tuple[bool, str]:
    success, error = await run_ffmpeg([
        "-i", input_path,
        "-vn",
        "-c:a", "libmp3lame",
        "-q:a", "2",
        "-ar", "44100",
        "-ac", "2",
        output_path,
    ])
    if not success and Path(output_path).exists():
        Path(output_path).unlink(missing_ok=True)
    return success, error
