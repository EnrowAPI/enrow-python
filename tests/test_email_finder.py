import asyncio
from unittest.mock import MagicMock

import pytest

from enrow import AsyncEnrow, Enrow

SEARCH_STARTED = {
    "message": "Single search operating",
    "id": "search_123",
    "credits_used": 1,
}


def _mock_client(**overrides):
    client = Enrow.__new__(Enrow)
    http = MagicMock()
    client._http = http
    from enrow.resources.email_finder import EmailFinder
    client.email = EmailFinder(http)
    return client, http


def test_find_sends_correct_body():
    client, http = _mock_client()
    http.post.return_value = SEARCH_STARTED

    result = client.email.find(
        company_domain="apple.com",
        full_name="Tim Cook",
    )

    http.post.assert_called_once_with("/email/find/single", {
        "company_domain": "apple.com",
        "fullname": "Tim Cook",
    })
    assert result["id"] == "search_123"


def test_get_by_id():
    client, http = _mock_client()
    http.get.return_value = {
        "email": "tcook@apple.com",
        "qualification": "valid",
    }

    result = client.email.get("search_123")

    http.get.assert_called_once_with("/email/find/single", id="search_123")
    assert result["email"] == "tcook@apple.com"


def test_find_bulk():
    client, http = _mock_client()
    http.post.return_value = {
        "message": "Bulk search operating",
        "id": "batch_xyz",
        "credits_used": 2,
        "estimated_duration": 1,
    }
    searches = [
        {"company_domain": "apple.com", "fullname": "Tim Cook"},
        {"company_domain": "microsoft.com", "fullname": "Satya Nadella"},
    ]

    result = client.email.find_bulk(searches=searches)

    http.post.assert_called_once_with("/email/find/bulk", {"searches": searches})
    assert result["id"] == "batch_xyz"


def test_find_with_polling():
    client, http = _mock_client()
    http.post.return_value = SEARCH_STARTED
    http.get.side_effect = [
        {"qualification": "ongoing"},
        {"qualification": "valid", "email": "tcook@apple.com"},
    ]

    result = client.email.find(
        company_domain="apple.com",
        full_name="Tim Cook",
        wait_for_result=True,
        poll_interval=0.01,
        timeout=5.0,
    )

    assert http.get.call_count == 2
    http.get.assert_called_with("/email/find/single", id="search_123")
    assert result == {"id": "search_123", "qualification": "valid", "email": "tcook@apple.com"}


def test_find_body_with_linkedin_url_company_info_and_custom(client, api):
    api.add("POST", "/email/find/single", 200, SEARCH_STARTED)

    search = client.email.find(
        linkedin_url="https://www.linkedin.com/in/dwight-schrute",
        custom={"crm_id": "lead_001"},
        settings={"country_code": "FR", "webhook": "https://example.com/hook"},
        retrieve_gender=True,
        retrieve_company_info=True,
    )

    request = api.calls("POST", "/email/find/single")[0]
    assert request["api_key"] == "test_key"
    assert request["json"] == {
        "linkedin_url": "https://www.linkedin.com/in/dwight-schrute",
        "custom": {"crm_id": "lead_001"},
        "settings": {
            "country_code": "FR",
            "webhook": "https://example.com/hook",
            "retrieve_gender": True,
            "retrieve_company_info": True,
        },
    }
    assert search["id"] == "search_123"


def test_find_wait_for_result_polls_get_until_final(client, api):
    api.add("POST", "/email/find/single", 200, SEARCH_STARTED)
    api.add("GET", "/email/find/single", 202, {"qualification": "ongoing"})
    api.add("GET", "/email/find/single", 202, {"qualification": "ongoing"})
    api.add("GET", "/email/find/single", 200, {
        "email": "dwight.schrute@dundermifflin.com",
        "qualification": "valid",
        "credits_used": 1,
    })

    result = client.email.find(
        full_name="Dwight Schrute",
        company_domain="dundermifflin.com",
        wait_for_result=True,
        poll_interval=0.001,
    )

    gets = api.calls("GET", "/email/find/single")
    assert len(gets) == 3
    assert all(r["params"] == {"id": "search_123"} for r in gets)
    assert result["id"] == "search_123"
    assert result["qualification"] == "valid"
    assert result["email"] == "dwight.schrute@dundermifflin.com"


def test_find_wait_for_result_returns_ongoing_with_id_at_timeout(client, api):
    api.add("POST", "/email/find/single", 200, SEARCH_STARTED)
    api.add("GET", "/email/find/single", 202, {"qualification": "ongoing"})

    result = client.email.find(
        full_name="Dwight Schrute",
        company_domain="dundermifflin.com",
        wait_for_result=True,
        poll_interval=0.001,
        timeout=0.02,
    )

    assert result == {"id": "search_123", "qualification": "ongoing"}
    assert len(api.calls("GET", "/email/find/single")) >= 1


def test_find_without_wait_does_not_poll(client, api):
    api.add("POST", "/email/find/single", 200, SEARCH_STARTED)

    result = client.email.find(full_name="Dwight Schrute", company_name="Dunder Mifflin")

    assert result == SEARCH_STARTED
    assert api.calls("GET", "/email/find/single") == []


def test_find_refuses_a_non_positive_poll_interval_before_starting_the_search(client, api):
    api.add("POST", "/email/find/single", 200, SEARCH_STARTED)

    with pytest.raises(ValueError):
        client.email.find(
            full_name="Dwight Schrute",
            company_domain="dundermifflin.com",
            wait_for_result=True,
            poll_interval=0,
        )

    assert api.requests == []


def test_get_bulk_reads_the_batch_id(client, api):
    api.add("POST", "/email/find/bulk", 201, {
        "message": "Bulk search operating",
        "id": "batch_1",
        "credits_used": 1,
        "estimated_duration": 1,
    })
    api.add("GET", "/email/find/bulk", 200, {"general": {"id": "batch_1", "status": "completed"}})

    batch = client.email.find_bulk(
        searches=[{"fullname": "Dwight Schrute", "company_domain": "dundermifflin.com"}],
        custom={"campaign": "q2"},
    )
    results = client.email.get_bulk(batch["id"])

    assert api.calls("POST", "/email/find/bulk")[0]["json"] == {
        "searches": [{"fullname": "Dwight Schrute", "company_domain": "dundermifflin.com"}],
        "custom": {"campaign": "q2"},
    }
    assert api.calls("GET", "/email/find/bulk")[0]["params"] == {"id": "batch_1"}
    assert results["general"]["status"] == "completed"


def test_async_find_wait_for_result(api):
    api.add("POST", "/email/find/single", 200, SEARCH_STARTED)
    api.add("GET", "/email/find/single", 202, {"qualification": "ongoing"})
    api.add("GET", "/email/find/single", 200, {"qualification": "invalid", "credits_used": 0})

    async def main():
        async with AsyncEnrow("test_key") as client:
            return await client.email.find(
                linkedin_url="https://www.linkedin.com/in/dwight-schrute",
                retrieve_company_info=True,
                wait_for_result=True,
                poll_interval=0.001,
            )

    result = asyncio.run(main())

    assert api.calls("POST", "/email/find/single")[0]["json"] == {
        "linkedin_url": "https://www.linkedin.com/in/dwight-schrute",
        "settings": {"retrieve_company_info": True},
    }
    assert len(api.calls("GET", "/email/find/single")) == 2
    assert result == {"id": "search_123", "qualification": "invalid", "credits_used": 0}
