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
    company_domain: str | None,
    company_name: str | None,
    full_name: str | None,
    linkedin_url: str | None,
    custom: dict | None,
    retrieve_gender: bool,
    retrieve_company_info: bool,
    settings: dict | None,
) -> dict[str, Any]:
    body: dict[str, Any] = {}
    if company_domain:
        body["company_domain"] = company_domain
    if company_name:
        body["company_name"] = company_name
    if full_name:
        body["fullname"] = full_name
    if linkedin_url:
        body["linkedin_url"] = linkedin_url
    if custom is not None:
        body["custom"] = custom

    merged_settings = dict(settings) if settings else {}
    if retrieve_gender:
        merged_settings["retrieve_gender"] = True
    if retrieve_company_info:
        merged_settings["retrieve_company_info"] = True
    if merged_settings:
        body["settings"] = merged_settings
    return body


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
        poll_interval: float = DEFAULT_INTERVAL,
        timeout: float = DEFAULT_TIMEOUT,
        *,
        linkedin_url: str | None = None,
        retrieve_company_info: bool = False,
    ) -> dict:
        """Start a single email search (``POST /email/find/single``).

        Search from ``full_name`` plus ``company_domain`` or ``company_name``,
        or from a LinkedIn profile URL with ``linkedin_url``. ``custom`` is a
        dict returned as-is with the result. ``settings`` takes ``webhook``,
        ``country_code``, ``retrieve_gender`` and ``retrieve_company_info``;
        the ``retrieve_gender`` and ``retrieve_company_info`` arguments set
        them too (company info is only returned with ``country_code="FR"``).

        Returns ``{"id", "message", "credits_used"}``: read the result with
        :meth:`get`. With ``wait_for_result=True``, polls :meth:`get` every
        ``poll_interval`` seconds until the result is final, for up to
        ``timeout`` seconds, and returns it with the search ``id``. If the
        search is still running at the timeout, the result has
        ``qualification == "ongoing"``: call :meth:`get` with its ``id`` later.
        """
        body = _single_search_body(
            company_domain=company_domain,
            company_name=company_name,
            full_name=full_name,
            linkedin_url=linkedin_url,
            custom=custom,
            retrieve_gender=retrieve_gender,
            retrieve_company_info=retrieve_company_info,
            settings=settings,
        )
        if wait_for_result:
            check_poll_interval(poll_interval)
        search = self._http.post("/email/find/single", body)
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
        return self._http.get("/email/find/single", id=id)

    def find_bulk(
        self,
        searches: list[dict],
        settings: dict | None = None,
        custom: dict | None = None,
    ) -> dict:
        """Start a bulk email search (``POST /email/find/bulk``).

        Each search uses the API field names: ``fullname`` plus
        ``company_domain`` or ``company_name``, and an optional ``custom``.
        Returns the batch ``id``: read the results with :meth:`get_bulk`.
        """
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
        poll_interval: float = DEFAULT_INTERVAL,
        timeout: float = DEFAULT_TIMEOUT,
        *,
        linkedin_url: str | None = None,
        retrieve_company_info: bool = False,
    ) -> dict:
        """Async version of :meth:`EmailFinder.find`."""
        body = _single_search_body(
            company_domain=company_domain,
            company_name=company_name,
            full_name=full_name,
            linkedin_url=linkedin_url,
            custom=custom,
            retrieve_gender=retrieve_gender,
            retrieve_company_info=retrieve_company_info,
            settings=settings,
        )
        if wait_for_result:
            check_poll_interval(poll_interval)
        search = await self._http.post("/email/find/single", body)
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
        return await self._http.get("/email/find/single", id=id)

    async def find_bulk(
        self,
        searches: list[dict],
        settings: dict | None = None,
        custom: dict | None = None,
    ) -> dict:
        """Async version of :meth:`EmailFinder.find_bulk`."""
        body: dict[str, Any] = {"searches": searches}
        if settings:
            body["settings"] = settings
        if custom is not None:
            body["custom"] = custom
        return await self._http.post("/email/find/bulk", body)

    async def get_bulk(self, id: str) -> dict:
        return await self._http.get("/email/find/bulk", id=id)
