import logging
from pathlib import Path
from typing import Optional
from mediasave.app.media.ffmpeg import run_ffmpeg

logger = logging.getLogger(__name__)


class AudioExtractor:
    def __init__(self, temp_dir: Path):
        self.temp_dir = temp_dir
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    async def extract(self, input_path: str, output_name: str = "extracted.mp3", sample_duration: int = 30) -> Optional[str]:
        input_file = Path(input_path)
        if not input_file.exists():
            return None

        output_path = self.temp_dir / output_name
        is_audio = input_file.suffix.lower() in {".mp3", ".m4a", ".wav", ".ogg", ".flac", ".aac", ".opus", ".weba", ".amr"}

        args = [
            "-i", str(input_file),
            "-ar", "44100",
            "-ac", "2",
            "-b:a", "192k",
        ]
        if not is_audio:
            args.extend(["-vn"])
        if sample_duration > 0:
            args.extend(["-t", str(sample_duration)])
        args.extend(["-y", str(output_path)])

        try:
            success, error = await run_ffmpeg(args)
            if success and output_path.exists():
                return str(output_path)
            if not success:
                logger.error("Audio extraction failed: %s", error)
            return None
        except Exception as e:
            logger.error("Audio extraction exception: %s", e)
            if output_path.exists():
                output_path.unlink(missing_ok=True)
            return None
