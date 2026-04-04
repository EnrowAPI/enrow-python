from unittest.mock import MagicMock
from enrow import Enrow


def _mock_client(**overrides):
    client = Enrow.__new__(Enrow)
    http = MagicMock()
    client._http = http
    from enrow.resources.email_finder import EmailFinder
    client.email = EmailFinder(http)
    return client, http


def test_find_sends_correct_body():
    client, http = _mock_client()
    http.post.return_value = {
        "id": "search_123",
        "status": "completed",
        "email": "tcook@apple.com",
        "qualification": "valid",
    }

    result = client.email.find(
        company_domain="apple.com",
        first_name="Tim",
        last_name="Cook",
    )

    http.post.assert_called_once_with("/email/find/single", {
        "company_domain": "apple.com",
        "first_name": "Tim",
        "last_name": "Cook",
    })
    assert result["email"] == "tcook@apple.com"


def test_get_by_id():
    client, http = _mock_client()
    http.get.return_value = {
        "id": "search_123",
        "status": "completed",
        "email": "tcook@apple.com",
    }

    result = client.email.get("search_123")

    http.get.assert_called_once_with("/email/find/single/search_123")
    assert result["email"] == "tcook@apple.com"


def test_find_bulk():
    client, http = _mock_client()
    http.post.return_value = {
        "batch_id": "batch_xyz",
        "total": 2,
        "status": "processing",
    }

    result = client.email.find_bulk(
        searches=[
            {"company_domain": "apple.com", "first_name": "Tim", "last_name": "Cook"},
            {"company_domain": "microsoft.com", "first_name": "Satya", "last_name": "Nadella"},
        ]
    )

    assert result["batch_id"] == "batch_xyz"
    assert result["total"] == 2


def test_find_with_polling():
    client, http = _mock_client()
    http.post.return_value = {"id": "search_123", "status": "pending"}
    http.get.side_effect = [
        {"id": "search_123", "status": "pending"},
        {"id": "search_123", "status": "completed", "email": "tcook@apple.com"},
    ]

    result = client.email.find(
        company_domain="apple.com",
        first_name="Tim",
        last_name="Cook",
        wait_for_result=True,
        poll_interval=0.01,
        timeout=5.0,
    )

    assert result["status"] == "completed"
    assert result["email"] == "tcook@apple.com"
