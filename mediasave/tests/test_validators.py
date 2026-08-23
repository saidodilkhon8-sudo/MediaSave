import pytest
from mediasave.app.downloaders.schemas import MediaInfo, PlatformType, MediaType


def test_media_info_creation():
    info = MediaInfo(
        url="https://youtube.com/watch?v=123",
        platform=PlatformType.YOUTUBE,
        media_type=MediaType.VIDEO,
        title="Test",
        duration=120.5,
        file_size=1024000,
    )
    assert info.platform == PlatformType.YOUTUBE
    assert info.media_type == MediaType.VIDEO
    assert info.duration == 120.5


def test_platform_type_values():
    assert PlatformType.YOUTUBE == "youtube"
    assert PlatformType.TIKTOK == "tiktok"
    assert PlatformType.INSTAGRAM == "instagram"


def test_media_type_values():
    assert MediaType.VIDEO == "video"
    assert MediaType.IMAGE == "image"
