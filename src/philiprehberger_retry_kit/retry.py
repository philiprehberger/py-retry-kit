from __future__ import annotations

import asyncio
import random
import time
from typing import TypeVar, Callable, Awaitable, Any

T = TypeVar("T")


class RetryError(Exception):
    def __init__(self, message: str, attempts: int, last_error: Exception) -> None:
        super().__init__(message)
        self.attempts = attempts
        self.last_error = last_error


def _calculate_delay(
    attempt: int,
    backoff: str,
    initial_delay: float,
    max_delay: float,
    jitter: bool,
) -> float:
    if backoff == "exponential":
        delay = initial_delay * (2 ** (attempt - 1))
    elif backoff == "linear":
        delay = initial_delay * attempt
    else:
        delay = initial_delay

    delay = min(delay, max_delay)

    if jitter:
        delay *= 0.5 + random.random() * 0.5

    return delay


def retry(
    fn: Callable[[], T],
    *,
    max_attempts: int = 3,
    backoff: str = "exponential",
    initial_delay: float = 1.0,
    max_delay: float = 30.0,
    jitter: bool = True,
    retry_on: Callable[[Exception], bool] | None = None,
    on_retry: Callable[[Exception, int], None] | None = None,
    on_success: Callable[[Any, int], None] | None = None,
    on_failure: Callable[[Exception, int], None] | None = None,
) -> T:
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")
    if backoff not in ("exponential", "linear", "fixed"):
        raise ValueError(f"Invalid backoff strategy: {backoff}")
    if initial_delay < 0:
        raise ValueError("initial_delay must be non-negative")

    last_error: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            result = fn()
            if on_success:
                on_success(result, attempt)
            return result
        except Exception as e:
            last_error = e

            if retry_on and not retry_on(e):
                raise

            if attempt < max_attempts:
                if on_retry:
                    on_retry(e, attempt)
                delay = _calculate_delay(attempt, backoff, initial_delay, max_delay, jitter)
                time.sleep(delay)

    if on_failure and last_error:
        on_failure(last_error, max_attempts)

    raise RetryError(
        f"All {max_attempts} attempts failed",
        max_attempts,
        last_error,  # type: ignore
    )


async def async_retry(
    fn: Callable[[], Awaitable[T]],
    *,
    max_attempts: int = 3,
    backoff: str = "exponential",
    initial_delay: float = 1.0,
    max_delay: float = 30.0,
    jitter: bool = True,
    retry_on: Callable[[Exception], bool] | None = None,
    on_retry: Callable[[Exception, int], None] | None = None,
    on_success: Callable[[Any, int], None] | None = None,
    on_failure: Callable[[Exception, int], None] | None = None,
) -> T:
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")
    if backoff not in ("exponential", "linear", "fixed"):
        raise ValueError(f"Invalid backoff strategy: {backoff}")
    if initial_delay < 0:
        raise ValueError("initial_delay must be non-negative")

    last_error: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            result = await fn()
            if on_success:
                on_success(result, attempt)
            return result
        except Exception as e:
            last_error = e

            if retry_on and not retry_on(e):
                raise

            if attempt < max_attempts:
                if on_retry:
                    on_retry(e, attempt)
                delay = _calculate_delay(attempt, backoff, initial_delay, max_delay, jitter)
                await asyncio.sleep(delay)

    if on_failure and last_error:
        on_failure(last_error, max_attempts)

    raise RetryError(
        f"All {max_attempts} attempts failed",
        max_attempts,
        last_error,  # type: ignore
    )
