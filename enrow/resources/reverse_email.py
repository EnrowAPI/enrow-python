from __future__ import annotations

from typing import Any
from ..utils.polling import poll_until_done, async_poll_until_done


class ReverseEmail:
    def __init__(self, http):
        self._http = http

    def find(
        self,
        email: str,
        settings: dict | None = None,
        wait_for_result: bool = False,
        poll_interval: float = 2.0,
        timeout: float = 30.0,
    ) -> dict:
        body: dict[str, Any] = {"email": email}
        if settings:
            body["settings"] = settings

        result = self._http.post("/reverse-email/single", body)

        if wait_for_result and result.get("status") in ("pending", "processing"):
            return poll_until_done(
                lambda: self.get(result["id"]),
                poll_interval=poll_interval,
                timeout=timeout,
            )

        return result

    def get(self, id: str) -> dict:
        return self._http.get(f"/reverse-email/single/{id}")

    def find_bulk(self, emails: list[dict], settings: dict | None = None) -> dict:
        body: dict[str, Any] = {"emails": emails}
        if settings:
            body["settings"] = settings
        return self._http.post("/reverse-email/bulk", body)

    def get_bulk(self, id: str) -> dict:
        return self._http.get(f"/reverse-email/bulk/{id}")


class AsyncReverseEmail:
    def __init__(self, http):
        self._http = http

    async def find(
        self,
        email: str,
        settings: dict | None = None,
        wait_for_result: bool = False,
        poll_interval: float = 2.0,
        timeout: float = 30.0,
    ) -> dict:
        body: dict[str, Any] = {"email": email}
        if settings:
            body["settings"] = settings

        result = await self._http.post("/reverse-email/single", body)

        if wait_for_result and result.get("status") in ("pending", "processing"):
            return await async_poll_until_done(
                lambda: self.get(result["id"]),
                poll_interval=poll_interval,
                timeout=timeout,
            )

        return result

    async def get(self, id: str) -> dict:
        return await self._http.get(f"/reverse-email/single/{id}")

    async def find_bulk(self, emails: list[dict], settings: dict | None = None) -> dict:
        body: dict[str, Any] = {"emails": emails}
        if settings:
            body["settings"] = settings
        return await self._http.post("/reverse-email/bulk", body)

    async def get_bulk(self, id: str) -> dict:
        return await self._http.get(f"/reverse-email/bulk/{id}")
