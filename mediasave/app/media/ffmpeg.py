import asyncio
import os
from pathlib import Path
from typing import Optional, Tuple
from mediasave.app.config import settings


async def run_ffmpeg(args: list[str], timeout: Optional[int] = None) -> Tuple[bool, str]:
    timeout = timeout or settings.ffmpeg_timeout
    cmd = [settings.ffmpeg_executable, "-y", "-loglevel", "error"] + args
    proc = None
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        output = (stdout or b"").decode("utf-8", errors="replace")
        error = (stderr or b"").decode("utf-8", errors="replace")
        return proc.returncode == 0, error or output
    except asyncio.TimeoutError:
        if proc is not None:
            try:
                proc.kill()
                await proc.wait()
            except ProcessLookupError:
                pass
            except Exception:
                pass
        return False, "FFmpeg timeout"
    except Exception as e:
        return False, str(e)


def get_video_duration(file_path: str) -> Optional[float]:
    try:
        import ffmpeg
        probe = ffmpeg.probe(file_path)
        video_stream = next((s for s in probe["streams"] if s["codec_type"] == "video"), None)
        if video_stream and "duration" in video_stream:
            return float(video_stream["duration"])
        return None
    except Exception:
        return None
