from abc import ABC, abstractmethod
from typing import Optional, Union, List
from mediasave.app.downloaders.schemas import MediaInfo, PlatformType, MediaType


class BaseDownloader(ABC):
    @abstractmethod
    def can_handle(self, url: str) -> bool:
        ...

    @abstractmethod
    async def get_info(self, url: str) -> MediaInfo:
        ...

    @abstractmethod
    async def download(self, url: str, output_dir: str, quality: str = "best") -> Union[str, List[str]]:
        ...
