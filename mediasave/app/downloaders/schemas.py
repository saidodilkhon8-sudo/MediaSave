from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum


class PlatformType(str, Enum):
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    YOUTUBE_SHORTS = "youtube_shorts"
    SNAPCHAT = "snapchat"
    LIKEE = "likee"
    PINTEREST = "pinterest"
    THREADS = "threads"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    REDDIT = "reddit"
    UNKNOWN = "unknown"


class MediaType(str, Enum):
    VIDEO = "video"
    IMAGE = "image"
    AUDIO = "audio"
    CAROUSEL = "carousel"
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
    entries: Optional[List["MediaInfo"]] = field(default_factory=list)
