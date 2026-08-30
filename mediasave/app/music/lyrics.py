import aiohttp
import logging
from mediasave.app.config import settings

logger = logging.getLogger(__name__)


async def fetch_lyrics(artist: str, title: str) -> str | None:
    try:
        query = f"{artist} {title}".strip()
        url = f"https://lrclib.net/api/search?q={aiohttp.helpers.requote_uri(query)}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=30) as response:
                if response.status != 200:
                    return None
                data = await response.json()
                if not data:
                    return None
                for item in data:
                    if item.get("syncedLyrics"):
                        return item["syncedLyrics"]
                for item in data:
                    if item.get("plainLyrics"):
                        return item["plainLyrics"]
                return None
    except Exception as e:
        logger.error(f"Lyrics fetch failed: {e}")
        return None
