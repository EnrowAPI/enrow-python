from __future__ import annotations

from .http import SyncHttpClient, AsyncHttpClient
from .resources.email_finder import EmailFinder, AsyncEmailFinder
from .resources.email_verifier import EmailVerifier, AsyncEmailVerifier
from .resources.phone_finder import PhoneFinder, AsyncPhoneFinder
from .resources.reverse_email import ReverseEmail, AsyncReverseEmail
from .resources.account import Account, AsyncAccount


class Enrow:
    def __init__(self, api_key: str, base_url: str | None = None):
        http = SyncHttpClient(api_key, base_url)
        self.email = EmailFinder(http)
        self.verify = EmailVerifier(http)
        self.phone = PhoneFinder(http)
        self.reverse_email = ReverseEmail(http)
        self.account = Account(http)
        self._http = http

    def close(self):
        self._http.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class AsyncEnrow:
    def __init__(self, api_key: str, base_url: str | None = None):
        http = AsyncHttpClient(api_key, base_url)
        self.email = AsyncEmailFinder(http)
        self.verify = AsyncEmailVerifier(http)
        self.phone = AsyncPhoneFinder(http)
        self.reverse_email = AsyncReverseEmail(http)
        self.account = AsyncAccount(http)
        self._http = http

    async def close(self):
        await self._http.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()
