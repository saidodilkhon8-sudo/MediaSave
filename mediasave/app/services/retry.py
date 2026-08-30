import asyncio
import logging
from typing import TypeVar, Callable, Awaitable
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

T = TypeVar("T")
logger = logging.getLogger(__name__)


class RetryableError(Exception):
    pass


def retry_async(fn: Callable[[], Awaitable[T]], max_attempts: int = 3, delay: float = 2, backoff: float = 2) -> T:
    @retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=delay, min=delay, max=delay * (backoff ** (max_attempts - 1))),
        retry=retry_if_exception_type(RetryableError),
        reraise=True,
    )
    async def _wrapped():
        try:
            return await fn()
        except Exception as e:
            if _is_retryable(e):
                logger.warning(f"Retryable error: {e}")
                raise RetryableError(e) from e
            raise

    return _wrapped()


def _is_retryable(error: Exception) -> bool:
    message = str(error).lower()
    retryable_signals = [
        "timeout",
        "timed out",
        "connection reset",
        "connection refused",
        "no internet",
        "socket error",
        "http error 5",
        "http error 429",
        "http error 403",
    ]
    return any(signal in message for signal in retryable_signals)
