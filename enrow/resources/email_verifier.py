from __future__ import annotations

from typing import Any


class EmailVerifier:
    def __init__(self, http):
        self._http = http

    def single(self, email: str, settings: dict | None = None) -> dict:
        body: dict[str, Any] = {"email": email}
        if settings:
            body["settings"] = settings
        return self._http.post("/email/verify/single", body)

    def get(self, id: str) -> dict:
        return self._http.get("/email/verify/single", id=id)

    def bulk(self, verifications: list[str], settings: dict | None = None, custom: dict | None = None) -> dict:
        body: dict[str, Any] = {"verifications": verifications}
        if settings:
            body["settings"] = settings
        if custom:
            body["custom"] = custom
        return self._http.post("/email/verify/bulk", body)

    def get_bulk(self, id: str) -> dict:
        return self._http.get("/email/verify/bulk", id=id)


class AsyncEmailVerifier:
    def __init__(self, http):
        self._http = http

    async def single(self, email: str, settings: dict | None = None) -> dict:
        body: dict[str, Any] = {"email": email}
        if settings:
            body["settings"] = settings
        return await self._http.post("/email/verify/single", body)

    async def get(self, id: str) -> dict:
        return await self._http.get("/email/verify/single", id=id)

    async def bulk(self, verifications: list[str], settings: dict | None = None, custom: dict | None = None) -> dict:
        body: dict[str, Any] = {"verifications": verifications}
        if settings:
            body["settings"] = settings
        if custom:
            body["custom"] = custom
        return await self._http.post("/email/verify/bulk", body)

    async def get_bulk(self, id: str) -> dict:
        return await self._http.get("/email/verify/bulk", id=id)
