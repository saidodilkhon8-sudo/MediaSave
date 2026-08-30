import logging
from typing import Optional
from mediasave.app.config import settings

logger = logging.getLogger(__name__)


def _platform_for_url(url: str) -> Optional[str]:
    lowered = url.lower()
    if "youtube.com" in lowered or "youtu.be" in lowered:
        return "youtube"
    if "instagram.com" in lowered or "instagr.am" in lowered:
        return "instagram"
    if "twitter.com" in lowered or "x.com" in lowered:
        return "twitter"
    if "threads.net" in lowered:
        return "threads"
    if "snapchat.com" in lowered or "snap.chat" in lowered:
        return "snapchat"
    if "reddit.com" in lowered or "redd.it" in lowered:
        return "reddit"
    if "pinterest.com" in lowered or "pin.it" in lowered:
        return "pinterest"
    if "likee.com" in lowered or "likee.video" in lowered:
        return "likee"
    if "facebook.com" in lowered or "fb.watch" in lowered:
        return "facebook"
    return None


def build_ytdlp_opts(url: str, extra: Optional[dict] = None) -> dict:
    platform = _platform_for_url(url)
    cookie_path = settings.platform_cookies_path(platform or "")
    cookies_used = False
    if cookie_path:
        cookies_used = True
        if platform and platform != "youtube":
            logger.warning("Using cookies for %s from %s", platform, cookie_path)
        else:
            logger.debug("Using cookies from %s", cookie_path)
    opts = {
        "quiet": True,
        "no_warnings": True,
        "verbose": False,
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        },
        "proxy": settings.proxy_url or None,
        "timeout": settings.download_timeout,
    }
    if cookie_path:
        opts["cookiefile"] = cookie_path
    if extra:
        opts.update({k: v for k, v in extra.items() if v is not None})
    logger.debug("yt-dlp opts for %s: cookies=%s, platform=%s, keys=%s", url, cookies_used, platform, sorted(opts.keys()))
    return opts
