from pathlib import Path
from mediasave.app.media.ffmpeg import run_ffmpeg
from mediasave.app.media.video_note import create_video_note
from mediasave.app.media.audio import extract_audio
from mediasave.app.media.thumbnail import create_thumbnail
from mediasave.app.config import settings
import logging

logger = logging.getLogger(__name__)


class MediaService:
    def __init__(self, temp_dir: Path):
        self.temp_dir = temp_dir
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    async def create_circle(self, input_path: str) -> tuple[str | None, str | None]:
        output = str(Path(self.temp_dir) / "circle.mp4")
        success, error = await create_video_note(input_path, output)
        if success:
            return output, None
        return None, error

    async def create_mp3(self, input_path: str) -> tuple[str | None, str | None]:
        output = str(Path(self.temp_dir) / "audio.mp3")
        success, error = await extract_audio(input_path, output)
        if success:
            return output, None
        return None, error

    async def create_thumbnail(self, input_path: str) -> tuple[str | None, str | None]:
        output = str(Path(self.temp_dir) / "thumb.jpg")
        success, error = await create_thumbnail(input_path, output)
        if success:
            return output, None
        return None, error

    async def add_watermark(self, input_path: str) -> tuple[str | None, str | None]:
        output = self.temp_dir / "watermarked.mp4"
        watermark = settings.watermark_text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
        success, error = await run_ffmpeg([
            "-i", input_path,
            "-vf", f"drawtext=text='{watermark}':fontcolor=white:fontsize=24:box=1:boxcolor=black@0.55:boxborderw=8:x=12:y=h-th-12",
            "-c:v", "libx264", "-preset", "fast", "-c:a", "copy", "-movflags", "+faststart",
            str(output),
        ])
        if success and output.is_file():
            return str(output), None
        return None, error or "Watermark failed"

    async def cut_video(self, input_path: str, start: str, end: str) -> tuple[str | None, str | None]:
        output = str(Path(self.temp_dir) / "cut.mp4")
        success, error = await run_ffmpeg([
            "-ss", start,
            "-to", end,
            "-i", input_path,
            "-c", "copy",
            output,
        ])
        if success and Path(output).is_file():
            return output, None
        return None, error or "Failed to cut video"

    async def compress_video(self, input_path: str, output_name: str = "compressed.mp4", max_size_mb: int = 50) -> tuple[str | None, str | None]:
        input_file = Path(input_path)
        if not input_file.exists():
            return None, "Input file not found"

        output_path = self.temp_dir / output_name
        target_bytes = max_size_mb * 1024 * 1024
        current_size = input_file.stat().st_size

        if current_size <= target_bytes:
            return input_path, None

        duration = get_video_duration(input_path)
        if not duration or duration <= 0:
            duration = 60

        target_bitrate = max(100, int((target_bytes * 8) / duration))

        success, error = await run_ffmpeg([
            "-i", str(input_file),
            "-vcodec", "libx264",
            "-preset", "fast",
            "-b:v", f"{target_bitrate}k",
            "-acodec", "aac",
            "-b:a", "128k",
            "-ar", "44100",
            "-ac", "2",
            "-movflags", "+faststart",
            "-y",
            str(output_path),
        ])

        if success and output_path.exists() and output_path.stat().st_size > 0:
            return str(output_path), None

        if output_path.exists():
            output_path.unlink(missing_ok=True)
        return None, error or "Compression failed"


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
