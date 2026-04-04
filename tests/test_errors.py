import pytest
import httpx
from unittest.mock import patch, MagicMock
from enrow import Enrow, AuthenticationError, InsufficientBalanceError, RateLimitError, EnrowError


def _make_response(status_code, json_data):
    response = MagicMock(spec=httpx.Response)
    response.status_code = status_code
    response.is_success = 200 <= status_code < 300
    response.reason_phrase = "Error"
    response.headers = {}
    response.json.return_value = json_data
    return response


def test_authentication_error():
    with patch("httpx.Client.post") as mock_post:
        mock_post.return_value = _make_response(401, {
            "error": "Unauthorized",
            "message": "Invalid API key",
        })

        client = Enrow("bad_key")
        with pytest.raises(AuthenticationError):
            client.email.find(company_domain="test.com")


def test_insufficient_balance_error():
    with patch("httpx.Client.post") as mock_post:
        mock_post.return_value = _make_response(402, {
            "error": "InsufficientBalance",
            "message": "Not enough credits",
        })

        client = Enrow("test_key")
        with pytest.raises(InsufficientBalanceError):
            client.email.find(company_domain="test.com")


def test_rate_limit_error():
    with patch("httpx.Client.post") as mock_post:
        mock_post.return_value = _make_response(429, {
            "error": "RateLimitExceeded",
            "message": "Rate limit exceeded",
        })

        client = Enrow("test_key")
        with pytest.raises(RateLimitError):
            client.email.find(company_domain="test.com")


def test_generic_error():
    with patch("httpx.Client.post") as mock_post:
        mock_post.return_value = _make_response(400, {
            "error": "ValidationError",
            "message": "Missing company_domain",
        })

        client = Enrow("test_key")
        with pytest.raises(EnrowError) as exc_info:
            client.email.find()
        assert exc_info.value.status == 400
