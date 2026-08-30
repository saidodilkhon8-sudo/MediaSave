import re
from typing import Optional
from mediasave.app.downloaders.schemas import PlatformType, MediaType, MediaInfo
from mediasave.app.downloaders.youtube import YouTubeDownloader
from mediasave.app.downloaders.instagram import InstagramDownloader
from mediasave.app.downloaders.twitter import TwitterDownloader
from mediasave.app.downloaders.facebook import FacebookDownloader
from mediasave.app.downloaders.reddit import RedditDownloader
from mediasave.app.downloaders.pinterest import PinterestDownloader
from mediasave.app.downloaders.snapchat import SnapchatDownloader
from mediasave.app.downloaders.likee import LikeeDownloader
from mediasave.app.downloaders.threads import ThreadsDownloader
from mediasave.app.downloaders.base import BaseDownloader


class PlatformDetector:
    def __init__(self):
        self.downloaders: list[BaseDownloader] = [
            YouTubeDownloader(),
            InstagramDownloader(),
            TwitterDownloader(),
            FacebookDownloader(),
            RedditDownloader(),
            PinterestDownloader(),
            SnapchatDownloader(),
            LikeeDownloader(),
            ThreadsDownloader(),
        ]
        self._platform_map = {
            YouTubeDownloader: PlatformType.YOUTUBE,
            InstagramDownloader: PlatformType.INSTAGRAM,
            TwitterDownloader: PlatformType.TWITTER,
            FacebookDownloader: PlatformType.FACEBOOK,
            RedditDownloader: PlatformType.REDDIT,
            PinterestDownloader: PlatformType.PINTEREST,
            SnapchatDownloader: PlatformType.SNAPCHAT,
            LikeeDownloader: PlatformType.LIKEE,
            ThreadsDownloader: PlatformType.THREADS,
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
