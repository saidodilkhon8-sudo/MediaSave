import pytest
import asyncio
from pathlib import Path
from mediasave.app.media.ffmpeg import run_ffmpeg, get_video_duration


@pytest.mark.asyncio
async def test_run_ffmpeg_invalid():
    success, error = await run_ffmpeg(["-invalid", "arg"], timeout=5)
    assert success is False


@pytest.mark.asyncio
async def test_get_video_duration_nonexistent():
    assert get_video_duration("/nonexistent/path.mp4") is None


@pytest.mark.asyncio
async def test_run_ffmpeg_timeout():
    success, error = await run_ffmpeg(["-f", "lavfi", "-i", "testsrc=duration=10:size=320x240:rate=30", "-t", "5", "-c:v", "libx264", "/dev/null"], timeout=1)
    assert success is False
