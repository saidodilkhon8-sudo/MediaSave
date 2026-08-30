import asyncio
from pathlib import Path
from mediasave.app.media.ffmpeg import run_ffmpeg


async def create_video_note(input_path: str, output_path: str) -> tuple[bool, str]:
    duration = get_video_duration(input_path)
    if duration and duration > 60:
        return False, "Video is too long for a Telegram circle (max 60s)"

    success, error = await run_ffmpeg([
        "-i", input_path,
        "-vf", "scale=512:512:force_original_aspect_ratio=decrease,pad=512:512:(ow-iw)/2:(oh-ih)/2",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        "-ar", "44100",
        "-ac", "2",
        "-shortest",
        "-movflags", "+faststart",
        output_path,
    ])
    return success, error


def get_video_duration(file_path: str) -> float | None:
    try:
        import ffmpeg
        probe = ffmpeg.probe(file_path)
        video_stream = next((s for s in probe["streams"] if s["codec_type"] == "video"), None)
        if video_stream and "duration" in video_stream:
            return float(video_stream["duration"])
        return None
    except Exception:
        return None
