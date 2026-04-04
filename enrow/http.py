from __future__ import annotations

import httpx
from .errors import EnrowError, AuthenticationError, InsufficientBalanceError, RateLimitError

BASE_URL = "https://api.enrow.io"


def _handle_error(response: httpx.Response) -> None:
    if response.is_success:
        return

    try:
        data = response.json()
    except Exception:
        data = {}

    message = data.get("message", response.reason_phrase)
    error = data.get("error", "UnknownError")

    if response.status_code == 401:
        raise AuthenticationError(message)
    elif response.status_code == 402:
        raise InsufficientBalanceError(message)
    elif response.status_code == 429:
        retry = response.headers.get("X-RateLimit-Reset")
        raise RateLimitError(message, int(retry) if retry else None)
    else:
        raise EnrowError(response.status_code, error, message)


class SyncHttpClient:
    def __init__(self, api_key: str, base_url: str | None = None):
        self._client = httpx.Client(
            base_url=base_url or BASE_URL,
            headers={"x-api-key": api_key, "Content-Type": "application/json"},
        )

    def get(self, path: str, **params) -> dict:
        response = self._client.get(path, params=params or None)
        _handle_error(response)
        return response.json()

    def post(self, path: str, body: dict) -> dict:
        response = self._client.post(path, json=body)
        _handle_error(response)
        return response.json()

    def close(self):
        self._client.close()


class AsyncHttpClient:
    def __init__(self, api_key: str, base_url: str | None = None):
        self._client = httpx.AsyncClient(
            base_url=base_url or BASE_URL,
            headers={"x-api-key": api_key, "Content-Type": "application/json"},
        )

    async def get(self, path: str, **params) -> dict:
        response = await self._client.get(path, params=params or None)
        _handle_error(response)
        return response.json()

    async def post(self, path: str, body: dict) -> dict:
        response = await self._client.post(path, json=body)
        _handle_error(response)
        return response.json()

    async def close(self):
        await self._client.aclose()
