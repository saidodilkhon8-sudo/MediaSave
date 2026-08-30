import asyncio
import shutil
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from mediasave.app.config import settings

logger = logging.getLogger(__name__)


async def cleanup_temp_files():
    while True:
        try:
            cutoff = datetime.now(timezone.utc) - timedelta(hours=settings.auto_delete_hours)
            for user_dir in settings.temp_path.iterdir():
                if user_dir.is_dir():
                    for item in user_dir.iterdir():
                        if item.stat().st_mtime < cutoff.timestamp():
                            if item.is_dir():
                                shutil.rmtree(item, ignore_errors=True)
                            else:
                                item.unlink(missing_ok=True)
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
        await asyncio.sleep(3600)
