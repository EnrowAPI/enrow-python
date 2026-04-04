class Account:
    def __init__(self, http):
        self._http = http

    def info(self) -> dict:
        return self._http.get("/account/info")


class AsyncAccount:
    def __init__(self, http):
        self._http = http

    async def info(self) -> dict:
        return await self._http.get("/account/info")
