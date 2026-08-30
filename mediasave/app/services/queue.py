import asyncio
from collections import defaultdict
from typing import Optional
from mediasave.app.config import settings


class DownloadQueue:
    def __init__(self):
        self._queues: dict[int, list[int]] = defaultdict(list)
        self._active: set[int] = set()
        self._lock = asyncio.Lock()

    def add(self, user_id: int) -> int:
        position = len(self._queues[user_id]) + 1
        self._queues[user_id].append(user_id)
        return position

    def remove(self, user_id: int) -> None:
        if user_id in self._queues and self._queues[user_id]:
            self._queues[user_id].pop(0)
        self._active.discard(user_id)

    def is_active(self, user_id: int) -> bool:
        return user_id in self._active

    async def acquire(self, user_id: int) -> bool:
        async with self._lock:
            if self.is_active(user_id):
                return False
            if len(self._active) >= settings.download_concurrency:
                return False
            self._active.add(user_id)
            self.remove(user_id)
            return True

    def release(self, user_id: int) -> None:
        self._active.discard(user_id)

    def size(self) -> int:
        return len(self._active) + sum(len(q) for q in self._queues.values())


class QueueFullError(Exception):
    pass
