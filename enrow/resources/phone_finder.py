from __future__ import annotations

from typing import Any
from ..utils.polling import (
    DEFAULT_INTERVAL,
    DEFAULT_TIMEOUT,
    async_poll_until_done,
    check_poll_interval,
    poll_until_done,
    with_id,
)


def _single_search_body(
    *,
    linkedin_url: str | None,
    first_name: str | None,
    last_name: str | None,
    company_domain: str | None,
    company_name: str | None,
    custom: str | dict | None,
    settings: dict | None,
) -> dict[str, Any]:
    body: dict[str, Any] = {}
    if linkedin_url:
        body["linkedin_url"] = linkedin_url
    if first_name:
        body["firstname"] = first_name
    if last_name:
        body["lastname"] = last_name
    if company_domain:
        body["company_domain"] = company_domain
    if company_name:
        body["company_name"] = company_name
    if custom is not None:
        body["custom"] = custom
    if settings:
        body["settings"] = settings
    return body


def _bulk_body(searches: list[dict], settings: dict | None, custom: dict | None) -> dict[str, Any]:
    body: dict[str, Any] = {"searches": searches}
    if settings:
        body["settings"] = settings
    if custom is not None:
        body["custom"] = custom
    return body


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
        custom: str | dict | None = None,
        settings: dict | None = None,
        wait_for_result: bool = False,
        poll_interval: float = DEFAULT_INTERVAL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> dict:
        """Start a single phone search (``POST /phone/single``).

        Search from ``linkedin_url`` (recommended, it prevails), or from
        ``first_name`` + ``last_name`` + ``company_domain`` or ``company_name``.
        ``settings`` takes ``webhook``.

        Returns the search ``id``: read the result with :meth:`get`. With
        ``wait_for_result=True``, polls :meth:`get` until the result is final,
        for up to ``timeout`` seconds, and returns it with the search ``id``
        (``qualification == "ongoing"`` if it is still running).
        """
        body = _single_search_body(
            linkedin_url=linkedin_url,
            first_name=first_name,
            last_name=last_name,
            company_domain=company_domain,
            company_name=company_name,
            custom=custom,
            settings=settings,
        )
        if wait_for_result:
            check_poll_interval(poll_interval)
        search = self._http.post("/phone/single", body)
        if not wait_for_result:
            return search

        search_id = search["id"]
        result = poll_until_done(
            lambda: self.get(search_id),
            poll_interval=poll_interval,
            timeout=timeout,
        )
        return with_id(result, search_id)

    def get(self, id: str) -> dict:
        return self._http.get("/phone/single", id=id)

    def find_bulk(
        self,
        searches: list[dict],
        settings: dict | None = None,
        custom: dict | None = None,
    ) -> dict:
        """Start a bulk phone search (``POST /phone/bulk``, up to 3,000 searches).

        Each search uses the API field names: ``linkedin_url``, or
        ``firstname`` + ``lastname`` + ``company_domain`` or ``company_name``,
        and an optional ``custom``. Returns the batch ``id``: read the results
        with :meth:`get_bulk`.
        """
        return self._http.post("/phone/bulk", _bulk_body(searches, settings, custom))

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
        custom: str | dict | None = None,
        settings: dict | None = None,
        wait_for_result: bool = False,
        poll_interval: float = DEFAULT_INTERVAL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> dict:
        """Async version of :meth:`PhoneFinder.find`."""
        body = _single_search_body(
            linkedin_url=linkedin_url,
            first_name=first_name,
            last_name=last_name,
            company_domain=company_domain,
            company_name=company_name,
            custom=custom,
            settings=settings,
        )
        if wait_for_result:
            check_poll_interval(poll_interval)
        search = await self._http.post("/phone/single", body)
        if not wait_for_result:
            return search

        search_id = search["id"]
        result = await async_poll_until_done(
            lambda: self.get(search_id),
            poll_interval=poll_interval,
            timeout=timeout,
        )
        return with_id(result, search_id)

    async def get(self, id: str) -> dict:
        return await self._http.get("/phone/single", id=id)

    async def find_bulk(
        self,
        searches: list[dict],
        settings: dict | None = None,
        custom: dict | None = None,
    ) -> dict:
        """Async version of :meth:`PhoneFinder.find_bulk`."""
        return await self._http.post("/phone/bulk", _bulk_body(searches, settings, custom))

    async def get_bulk(self, id: str) -> dict:
        return await self._http.get("/phone/bulk", id=id)
