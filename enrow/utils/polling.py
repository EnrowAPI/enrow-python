from __future__ import annotations

import time
import asyncio
from typing import Callable, Awaitable, TypeVar

T = TypeVar("T", bound=dict)

PENDING_STATES = {"pending", "processing", "ongoing"}
DEFAULT_INTERVAL = 2.0
DEFAULT_TIMEOUT = 30.0


def poll_until_done(
    fetcher: Callable[[], T],
    *,
    status_key: str = "status",
    poll_interval: float = DEFAULT_INTERVAL,
    timeout: float = DEFAULT_TIMEOUT,
) -> T:
    start = time.monotonic()
    while True:
        result = fetcher()
        if result.get(status_key, "") not in PENDING_STATES:
            return result
        if time.monotonic() - start >= timeout:
            return result
        time.sleep(poll_interval)


async def async_poll_until_done(
    fetcher: Callable[[], Awaitable[T]],
    *,
    status_key: str = "status",
    poll_interval: float = DEFAULT_INTERVAL,
    timeout: float = DEFAULT_TIMEOUT,
) -> T:
    start = time.monotonic()
    while True:
        result = await fetcher()
        if result.get(status_key, "") not in PENDING_STATES:
            return result
        if time.monotonic() - start >= timeout:
            return result
        await asyncio.sleep(poll_interval)
