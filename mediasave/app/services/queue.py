import asyncio
import logging
from typing import Callable, Awaitable, Optional
from mediasave.app.config import settings

logger = logging.getLogger(__name__)


class DownloadQueue:
    def __init__(self, max_size: int = None):
        self.max_size = max_size or settings.max_queue_size
        self._queue: asyncio.Queue = asyncio.Queue(maxsize=self.max_size)
        self._processing = False
        self._lock = asyncio.Lock()

    async def enqueue(self, task: Callable[[], Awaitable[None]]) -> int:
        async with self._lock:
            position = self._queue.qsize() + 1
            await self._queue.put(task)
            if not self._processing:
                self._processing = True
                asyncio.create_task(self._process())
            return position

    async def _process(self):
        while not self._queue.empty():
            task = await self._queue.get()
            try:
                await task()
            except Exception:
                logger.exception("Queued task failed")
            self._queue.task_done()
        async with self._lock:
            self._processing = False

    @property
    def size(self) -> int:
        return self._queue.qsize()
