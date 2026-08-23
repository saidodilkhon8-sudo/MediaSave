import pytest
import asyncio
from pathlib import Path
from mediasave.app.media.video_note import create_video_note


@pytest.mark.asyncio
async def test_create_video_note_invalid_path():
    success, error = await create_video_note("/nonexistent.mp4", "/tmp/test_circle.mp4")
    assert success is False
    assert error is not None
