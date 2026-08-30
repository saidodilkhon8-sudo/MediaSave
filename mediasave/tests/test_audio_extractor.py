import pytest
import os
from pathlib import Path
from unittest.mock import patch
from mediasave.app.media.audio_extractor import AudioExtractor


@pytest.fixture
def extractor(tmp_path):
    return AudioExtractor(tmp_path)


@pytest.mark.asyncio
async def test_extract_nonexistent_file(extractor):
    result = await extractor.extract("/nonexistent.mp3")
    assert result is None


@pytest.mark.asyncio
async def test_extract_mp3(extractor, tmp_path):
    mp3_file = tmp_path / "test.mp3"
    mp3_file.write_bytes(b"fake mp3 content")

    async def mock_run_ffmpeg(args):
        output = Path(args[-1])
        output.write_bytes(b"fake audio")
        return True, ""

    with patch("mediasave.app.media.audio_extractor.run_ffmpeg", side_effect=mock_run_ffmpeg):
        result = await extractor.extract(str(mp3_file), "output.mp3", sample_duration=30)

    assert result is not None
    assert result.endswith("output.mp3")


@pytest.mark.asyncio
async def test_extract_video(extractor, tmp_path):
    video_file = tmp_path / "test.mp4"
    video_file.write_bytes(b"fake mp4 content")

    async def mock_run_ffmpeg(args):
        output = Path(args[-1])
        output.write_bytes(b"fake audio")
        return True, ""

    with patch("mediasave.app.media.audio_extractor.run_ffmpeg", side_effect=mock_run_ffmpeg) as mock_ffmpeg:
        result = await extractor.extract(str(video_file), "output.mp3", sample_duration=30)

    assert result is not None
    assert result.endswith("output.mp3")
    args = mock_ffmpeg.call_args[0][0]
    assert "-vn" in args


@pytest.mark.asyncio
async def test_extract_ffmpeg_failure(extractor, tmp_path):
    mp3_file = tmp_path / "test.mp3"
    mp3_file.write_bytes(b"fake mp3 content")

    async def mock_run_ffmpeg_fail(args):
        return False, "ffmpeg error"

    with patch("mediasave.app.media.audio_extractor.run_ffmpeg", side_effect=mock_run_ffmpeg_fail):
        result = await extractor.extract(str(mp3_file), "output.mp3", sample_duration=30)

    assert result is None


@pytest.mark.asyncio
async def test_extract_cleanup(extractor, tmp_path):
    mp3_file = tmp_path / "test.mp3"
    mp3_file.write_bytes(b"fake mp3 content")

    async def mock_run_ffmpeg_fail(args):
        return False, "error"

    with patch("mediasave.app.media.audio_extractor.run_ffmpeg", side_effect=mock_run_ffmpeg_fail):
        result = await extractor.extract(str(mp3_file), "output.mp3", sample_duration=30)

    assert result is None
    output_path = tmp_path / "output.mp3"
    assert not output_path.exists()
