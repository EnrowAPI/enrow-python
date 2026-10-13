from __future__ import annotations

import json
from collections import deque

import httpx
import pytest

from enrow import Enrow


class FakeApi:
    """Stands in for api.enrow.io: records each request and answers with the
    responses queued for its method and path (the last one keeps repeating)."""

    def __init__(self):
        self.requests: list[dict] = []
        self._responses: dict[tuple[str, str], deque] = {}

    def add(self, method: str, path: str, status: int = 200, body: dict | None = None) -> None:
        queue = self._responses.setdefault((method, path), deque())
        queue.append((status, body if body is not None else {}))

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(
            {
                "method": request.method,
                "path": request.url.path,
                "params": dict(request.url.params),
                "json": json.loads(request.content) if request.content else None,
                "api_key": request.headers.get("x-api-key"),
            }
        )
        queue = self._responses.get((request.method, request.url.path))
        if not queue:
            return httpx.Response(500, json={"message": "no fake response"})
        status, body = queue.popleft() if len(queue) > 1 else queue[0]
        return httpx.Response(status, json=body)

    def calls(self, method: str, path: str) -> list[dict]:
        return [r for r in self.requests if r["method"] == method and r["path"] == path]


@pytest.fixture
def api(monkeypatch):
    """Routes every httpx client the SDK creates to a FakeApi."""
    fake = FakeApi()
    transport = httpx.MockTransport(fake.handler)
    real_client, real_async_client = httpx.Client, httpx.AsyncClient
    monkeypatch.setattr(httpx, "Client", lambda **kw: real_client(transport=transport, **kw))
    monkeypatch.setattr(
        httpx, "AsyncClient", lambda **kw: real_async_client(transport=transport, **kw)
    )
    return fake


@pytest.fixture
def client(api):
    with Enrow("test_key") as client:
        yield client
