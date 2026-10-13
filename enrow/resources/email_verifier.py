from __future__ import annotations

import warnings
from typing import Any


def _bulk_body(
    verifications: list[str] | None,
    emails: list[str] | None,
    settings: dict | None,
    custom: dict | None,
) -> dict[str, Any]:
    if emails is not None:
        if verifications is not None:
            raise TypeError("bulk() takes `verifications` or `emails`, not both")
        warnings.warn(
            "bulk(emails=...) is deprecated, use bulk(verifications=...)",
            DeprecationWarning,
            stacklevel=3,
        )
        verifications = emails
    if verifications is None:
        raise TypeError("bulk() missing required argument: 'verifications'")
    if isinstance(verifications, str):
        raise TypeError("verifications must be a list of email addresses, not a string")

    body: dict[str, Any] = {"verifications": list(verifications)}
    if settings:
        body["settings"] = settings
    if custom is not None:
        body["custom"] = custom
    return body


class EmailVerifier:
    def __init__(self, http):
        self._http = http

    def single(self, email: str, settings: dict | None = None, custom: dict | None = None) -> dict:
        body: dict[str, Any] = {"email": email}
        if settings:
            body["settings"] = settings
        if custom is not None:
            body["custom"] = custom
        return self._http.post("/email/verify/single", body)

    def get(self, id: str) -> dict:
        return self._http.get("/email/verify/single", id=id)

    def bulk(
        self,
        verifications: list[str] | None = None,
        settings: dict | None = None,
        custom: dict | None = None,
        *,
        emails: list[str] | None = None,
    ) -> dict:
        """Start a bulk verification (``POST /email/verify/bulk``).

        ``verifications`` is the list of email addresses to verify (up to
        5,000). ``emails`` is a deprecated alias. Returns the batch ``id``:
        read the results with :meth:`get_bulk`.
        """
        body = _bulk_body(verifications, emails, settings, custom)
        return self._http.post("/email/verify/bulk", body)

    def get_bulk(self, id: str) -> dict:
        return self._http.get("/email/verify/bulk", id=id)


class AsyncEmailVerifier:
    def __init__(self, http):
        self._http = http

    async def single(self, email: str, settings: dict | None = None, custom: dict | None = None) -> dict:
        body: dict[str, Any] = {"email": email}
        if settings:
            body["settings"] = settings
        if custom is not None:
            body["custom"] = custom
        return await self._http.post("/email/verify/single", body)

    async def get(self, id: str) -> dict:
        return await self._http.get("/email/verify/single", id=id)

    async def bulk(
        self,
        verifications: list[str] | None = None,
        settings: dict | None = None,
        custom: dict | None = None,
        *,
        emails: list[str] | None = None,
    ) -> dict:
        """Async version of :meth:`EmailVerifier.bulk`."""
        body = _bulk_body(verifications, emails, settings, custom)
        return await self._http.post("/email/verify/bulk", body)

    async def get_bulk(self, id: str) -> dict:
        return await self._http.get("/email/verify/bulk", id=id)
