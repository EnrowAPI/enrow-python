from __future__ import annotations

from typing import Any
from ..utils.polling import poll_until_done, async_poll_until_done


class PhoneFinder:
    def __init__(self, http):
        self._http = http

    def find(
        self,
        linkedin_url: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        company_domain: str | None = None,
        company_name: str | None = None,
        custom: str | None = None,
        settings: dict | None = None,
        wait_for_result: bool = False,
        poll_interval: float = 2.0,
        timeout: float = 30.0,
    ) -> dict:
        body: dict[str, Any] = {}
        if linkedin_url:
            body["linkedin_url"] = linkedin_url
        if first_name:
            body["first_name"] = first_name
        if last_name:
            body["last_name"] = last_name
        if company_domain:
            body["company_domain"] = company_domain
        if company_name:
            body["company_name"] = company_name
        if custom is not None:
            body["custom"] = custom
        if settings:
            body["settings"] = settings

        result = self._http.post("/phone/single", body)

        if wait_for_result:
            return poll_until_done(
                lambda: self.get(result["id"]),
                status_key="qualification",
                poll_interval=poll_interval,
                timeout=timeout,
            )

        return result

    def get(self, id: str) -> dict:
        return self._http.get("/phone/single", id=id)

    def find_bulk(self, searches: list[dict], settings: dict | None = None) -> dict:
        body: dict[str, Any] = {"searches": searches}
        if settings:
            body["settings"] = settings
        return self._http.post("/phone/bulk", body)

    def get_bulk(self, id: str) -> dict:
        return self._http.get("/phone/bulk", id=id)


class AsyncPhoneFinder:
    def __init__(self, http):
        self._http = http

    async def find(
        self,
        linkedin_url: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        company_domain: str | None = None,
        company_name: str | None = None,
        custom: str | None = None,
        settings: dict | None = None,
        wait_for_result: bool = False,
        poll_interval: float = 2.0,
        timeout: float = 30.0,
    ) -> dict:
        body: dict[str, Any] = {}
        if linkedin_url:
            body["linkedin_url"] = linkedin_url
        if first_name:
            body["first_name"] = first_name
        if last_name:
            body["last_name"] = last_name
        if company_domain:
            body["company_domain"] = company_domain
        if company_name:
            body["company_name"] = company_name
        if custom is not None:
            body["custom"] = custom
        if settings:
            body["settings"] = settings

        result = await self._http.post("/phone/single", body)

        if wait_for_result:
            return await async_poll_until_done(
                lambda: self.get(result["id"]),
                status_key="qualification",
                poll_interval=poll_interval,
                timeout=timeout,
            )

        return result

    async def get(self, id: str) -> dict:
        return await self._http.get("/phone/single", id=id)

    async def find_bulk(self, searches: list[dict], settings: dict | None = None) -> dict:
        body: dict[str, Any] = {"searches": searches}
        if settings:
            body["settings"] = settings
        return await self._http.post("/phone/bulk", body)

    async def get_bulk(self, id: str) -> dict:
        return await self._http.get("/phone/bulk", id=id)
