import re
from typing import Optional
from mediasave.app.downloaders.schemas import PlatformType, MediaType, MediaInfo
from mediasave.app.downloaders.youtube import YouTubeDownloader
from mediasave.app.downloaders.tiktok import TikTokDownloader
from mediasave.app.downloaders.instagram import InstagramDownloader
from mediasave.app.downloaders.twitter import TwitterDownloader
from mediasave.app.downloaders.facebook import FacebookDownloader
from mediasave.app.downloaders.base import BaseDownloader


class PlatformDetector:
    def __init__(self):
        self.downloaders: list[BaseDownloader] = [
            YouTubeDownloader(),
            TikTokDownloader(),
            InstagramDownloader(),
            TwitterDownloader(),
            FacebookDownloader(),
        ]
        self._platform_map = {
            YouTubeDownloader: PlatformType.YOUTUBE,
            TikTokDownloader: PlatformType.TIKTOK,
            InstagramDownloader: PlatformType.INSTAGRAM,
            TwitterDownloader: PlatformType.TWITTER,
            FacebookDownloader: PlatformType.FACEBOOK,
        }

    def detect(self, url: str) -> tuple[Optional[PlatformType], Optional[BaseDownloader]]:
        for downloader in self.downloaders:
            if downloader.can_handle(url):
                platform = self._platform_map.get(type(downloader), PlatformType.UNKNOWN)
                if isinstance(downloader, YouTubeDownloader):
                    if "/shorts/" in url:
                        platform = PlatformType.YOUTUBE_SHORTS
                return platform, downloader
        return PlatformType.UNKNOWN, None

    def get_downloader(self, url: str) -> Optional[BaseDownloader]:
        for downloader in self.downloaders:
            if downloader.can_handle(url):
                return downloader
        return None
