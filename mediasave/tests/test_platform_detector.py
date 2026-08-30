import pytest
from mediasave.app.services.platform_detector import PlatformDetector
from mediasave.app.downloaders.schemas import PlatformType, MediaType
from mediasave.app.i18n import get_text, load_translations
from mediasave.app.config import settings


@pytest.fixture
def detector():
    return PlatformDetector()


class TestPlatformDetector:
    def test_instagram_detection(self, detector):
        platform, downloader = detector.detect("https://www.instagram.com/reel/abc123")
        assert platform == PlatformType.INSTAGRAM
        assert downloader is not None

    def test_youtube_detection(self, detector):
        platform, downloader = detector.detect("https://www.youtube.com/watch?v=123")
        assert platform == PlatformType.YOUTUBE
        assert downloader is not None

    def test_youtube_short_detection(self, detector):
        platform, downloader = detector.detect("https://www.youtube.com/shorts/abc123")
        assert platform == PlatformType.YOUTUBE_SHORTS
        assert downloader is not None

    def test_twitter_detection(self, detector):
        platform, downloader = detector.detect("https://twitter.com/user/status/123")
        assert platform == PlatformType.TWITTER
        assert downloader is not None

    def test_facebook_detection(self, detector):
        platform, downloader = detector.detect("https://www.facebook.com/watch/?v=123")
        assert platform == PlatformType.FACEBOOK
        assert downloader is not None

    def test_reddit_detection(self, detector):
        platform, downloader = detector.detect("https://www.reddit.com/r/videos/comments/abc")
        assert platform == PlatformType.REDDIT
        assert downloader is not None

    def test_pinterest_detection(self, detector):
        platform, downloader = detector.detect("https://www.pinterest.com/pin/123")
        assert platform == PlatformType.PINTEREST
        assert downloader is not None

    def test_pinterest_short_detection(self, detector):
        platform, downloader = detector.detect("https://pin.it/abc")
        assert platform == PlatformType.PINTEREST
        assert downloader is not None

    def test_snapchat_detection(self, detector):
        platform, downloader = detector.detect("https://www.snapchat.com/discover/abc")
        assert platform == PlatformType.SNAPCHAT
        assert downloader is not None

    def test_likee_detection(self, detector):
        platform, downloader = detector.detect("https://likee.video/video/abc")
        assert platform == PlatformType.LIKEE
        assert downloader is not None

    def test_threads_detection(self, detector):
        platform, downloader = detector.detect("https://www.threads.net/@user/post/abc")
        assert platform == PlatformType.THREADS
        assert downloader is not None

    def test_tiktok_unsupported(self, detector):
        platform, downloader = detector.detect("https://tiktok.com/@user/video/123")
        assert platform == PlatformType.UNKNOWN
        assert downloader is None

    def test_unknown_platform(self, detector):
        platform, downloader = detector.detect("https://unknown.com/video")
        assert platform == PlatformType.UNKNOWN
        assert downloader is None

    def test_invalid_url(self, detector):
        platform, downloader = detector.detect("not a url")
        assert platform == PlatformType.UNKNOWN
        assert downloader is None


class TestI18n:
    def test_russian_texts(self):
        load_translations()
        assert "MediaSave" in get_text("ru", "start_message")
        assert "Скачать" in get_text("ru", "menu_download")

    def test_english_texts(self):
        load_translations()
        assert "MediaSave" in get_text("en", "start_message")
        assert "Download" in get_text("en", "menu_download")

    def test_uzbek_texts(self):
        load_translations()
        assert "MediaSave" in get_text("uz", "start_message")
        assert "Yuklash" in get_text("uz", "menu_download")

    def test_fallback_to_key(self):
        load_translations()
        assert get_text("ru", "nonexistent_key") == "nonexistent_key"


class TestValidators:
    def test_media_info_creation(self):
        from mediasave.app.downloaders.schemas import MediaInfo
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

    def test_platform_type_values(self):
        assert PlatformType.YOUTUBE == "youtube"
        assert PlatformType.INSTAGRAM == "instagram"
        assert PlatformType.TWITTER == "twitter"
        assert PlatformType.FACEBOOK == "facebook"
        assert PlatformType.REDDIT == "reddit"
        assert PlatformType.PINTEREST == "pinterest"

    def test_media_type_values(self):
        assert MediaType.VIDEO == "video"
        assert MediaType.IMAGE == "image"
