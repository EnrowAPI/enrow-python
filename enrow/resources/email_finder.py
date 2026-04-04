from __future__ import annotations

from typing import Any
from ..utils.polling import poll_until_done, async_poll_until_done


class EmailFinder:
    def __init__(self, http):
        self._http = http

    def find(
        self,
        company_domain: str | None = None,
        company_name: str | None = None,
        full_name: str | None = None,
        custom: dict | None = None,
        retrieve_gender: bool = False,
        settings: dict | None = None,
        wait_for_result: bool = False,
        poll_interval: float = 2.0,
        timeout: float = 30.0,
    ) -> dict:
        body: dict[str, Any] = {}
        if company_domain:
            body["company_domain"] = company_domain
        if company_name:
            body["company_name"] = company_name
        if full_name:
            body["fullname"] = full_name
        if custom is not None:
            body["custom"] = custom

        merged_settings = dict(settings) if settings else {}
        if retrieve_gender:
            merged_settings["retrieve_gender"] = True
        if merged_settings:
            body["settings"] = merged_settings

        result = self._http.post("/email/find/single", body)

        if wait_for_result and result.get("status") == "pending":
            return poll_until_done(
                lambda: self.get(result["id"]),
                poll_interval=poll_interval,
                timeout=timeout,
            )

        return result

    def get(self, id: str) -> dict:
        return self._http.get("/email/find/single", id=id)

    def find_bulk(
        self,
        searches: list[dict],
        settings: dict | None = None,
        custom: dict | None = None,
    ) -> dict:
        body: dict[str, Any] = {"searches": searches}
        if settings:
            body["settings"] = settings
        if custom is not None:
            body["custom"] = custom
        return self._http.post("/email/find/bulk", body)

    def get_bulk(self, id: str) -> dict:
        return self._http.get("/email/find/bulk", id=id)


class AsyncEmailFinder:
    def __init__(self, http):
        self._http = http

    async def find(
        self,
        company_domain: str | None = None,
        company_name: str | None = None,
        full_name: str | None = None,
        custom: dict | None = None,
        retrieve_gender: bool = False,
        settings: dict | None = None,
        wait_for_result: bool = False,
        poll_interval: float = 2.0,
        timeout: float = 30.0,
    ) -> dict:
        body: dict[str, Any] = {}
        if company_domain:
            body["company_domain"] = company_domain
        if company_name:
            body["company_name"] = company_name
        if full_name:
            body["fullname"] = full_name
        if custom is not None:
            body["custom"] = custom

        merged_settings = dict(settings) if settings else {}
        if retrieve_gender:
            merged_settings["retrieve_gender"] = True
        if merged_settings:
            body["settings"] = merged_settings

        result = await self._http.post("/email/find/single", body)

        if wait_for_result and result.get("status") == "pending":
            return await async_poll_until_done(
                lambda: self.get(result["id"]),
                poll_interval=poll_interval,
                timeout=timeout,
            )

        return result

    async def get(self, id: str) -> dict:
        return await self._http.get("/email/find/single", id=id)

    async def find_bulk(
        self,
        searches: list[dict],
        settings: dict | None = None,
        custom: dict | None = None,
    ) -> dict:
        body: dict[str, Any] = {"searches": searches}
        if settings:
            body["settings"] = settings
        if custom is not None:
            body["custom"] = custom
        return await self._http.post("/email/find/bulk", body)

    async def get_bulk(self, id: str) -> dict:
        return await self._http.get("/email/find/bulk", id=id)
