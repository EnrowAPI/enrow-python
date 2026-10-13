from __future__ import annotations

import time
import asyncio
from typing import Callable, Awaitable, TypeVar

T = TypeVar("T", bound=dict)

# The single GET endpoints answer `{"qualification": "ongoing"}` (HTTP 202)
# until the result is final.
PENDING_STATES = {"pending", "processing", "ongoing"}
DEFAULT_INTERVAL = 2.0
DEFAULT_TIMEOUT = 30.0


def check_poll_interval(poll_interval: float) -> None:
    """Refuses an interval that would poll the API in a tight loop."""
    if poll_interval <= 0:
        raise ValueError("poll_interval must be greater than 0")


def with_id(result: dict, search_id: str) -> dict:
    """The GET result with the id of the search, which it does not carry."""
    return {"id": search_id, **result}


def poll_until_done(
    fetcher: Callable[[], T],
    *,
    status_key: str = "qualification",
    poll_interval: float = DEFAULT_INTERVAL,
    timeout: float = DEFAULT_TIMEOUT,
) -> T:
    """Wait ``poll_interval`` seconds, call ``fetcher``, and repeat until
    ``result[status_key]`` is final or ``timeout`` seconds have passed.

    Returns the last result: after a timeout, it is still pending
    (``qualification == "ongoing"``).
    """
    check_poll_interval(poll_interval)
    start = time.monotonic()
    while True:
        time.sleep(poll_interval)
        result = fetcher()
        if result.get(status_key, "") not in PENDING_STATES:
            return result
        if time.monotonic() - start >= timeout:
            return result


async def async_poll_until_done(
    fetcher: Callable[[], Awaitable[T]],
    *,
    status_key: str = "qualification",
    poll_interval: float = DEFAULT_INTERVAL,
    timeout: float = DEFAULT_TIMEOUT,
) -> T:
    """Async version of :func:`poll_until_done`."""
    check_poll_interval(poll_interval)
    start = time.monotonic()
    while True:
        await asyncio.sleep(poll_interval)
        result = await fetcher()
        if result.get(status_key, "") not in PENDING_STATES:
            return result
        if time.monotonic() - start >= timeout:
            return result
