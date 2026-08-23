from dataclasses import dataclass
from typing import Optional
from enum import Enum


class PlatformType(str, Enum):
    YOUTUBE = "youtube"
    YOUTUBE_SHORTS = "youtube_shorts"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    UNKNOWN = "unknown"


class MediaType(str, Enum):
    VIDEO = "video"
    IMAGE = "image"
    AUDIO = "audio"
    UNKNOWN = "unknown"


@dataclass
class MediaInfo:
    url: str
    platform: PlatformType
    media_type: MediaType
    title: Optional[str] = None
    duration: Optional[float] = None
    file_size: Optional[int] = None
    thumbnail_url: Optional[str] = None
    uploader: Optional[str] = None
    original_url: Optional[str] = None
