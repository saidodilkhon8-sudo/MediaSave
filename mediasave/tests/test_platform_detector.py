import pytest
from mediasave.app.services.platform_detector import PlatformDetector
from mediasave.app.downloaders.schemas import PlatformType


@pytest.fixture
def detector():
    return PlatformDetector()


def test_youtube_detection(detector):
    platform, downloader = detector.detect("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert platform == PlatformType.YOUTUBE
    assert downloader is not None


def test_youtube_short_detection(detector):
    platform, downloader = detector.detect("https://www.youtube.com/shorts/abc123")
    assert platform == PlatformType.YOUTUBE_SHORTS
    assert downloader is not None


def test_tiktok_detection(detector):
    platform, downloader = detector.detect("https://www.tiktok.com/@user/video/123")
    assert platform == PlatformType.TIKTOK
    assert downloader is not None


def test_instagram_detection(detector):
    platform, downloader = detector.detect("https://www.instagram.com/p/ABC123/")
    assert platform == PlatformType.INSTAGRAM
    assert downloader is not None


def test_twitter_detection(detector):
    platform, downloader = detector.detect("https://twitter.com/user/status/123")
    assert platform == PlatformType.TWITTER
    assert downloader is not None


def test_facebook_detection(detector):
    platform, downloader = detector.detect("https://www.facebook.com/watch/?v=123")
    assert platform == PlatformType.FACEBOOK
    assert downloader is not None


def test_unknown_platform(detector):
    platform, downloader = detector.detect("https://unknown.example.com/video")
    assert platform == PlatformType.UNKNOWN
    assert downloader is None


def test_invalid_url(detector):
    platform, downloader = detector.detect("not_a_url")
    assert platform == PlatformType.UNKNOWN
    assert downloader is None
