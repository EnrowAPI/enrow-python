import asyncio

import pytest

from enrow import AsyncEnrow

BULK_STARTED = {
    "message": "Bulk verification operating",
    "id": "batch_1",
    "credits_used": 0.5,
    "estimated_duration": 1,
}
EMAILS = ["pam.beesly@dundermifflin.com", "angela.martin@dundermifflin.com"]


def test_bulk_sends_verifications(client, api):
    api.add("POST", "/email/verify/bulk", 201, BULK_STARTED)

    batch = client.verify.bulk(
        verifications=EMAILS,
        settings={"webhook": "https://example.com/hook"},
        custom={"campaign": "q2"},
    )

    assert api.calls("POST", "/email/verify/bulk")[0]["json"] == {
        "verifications": EMAILS,
        "settings": {"webhook": "https://example.com/hook"},
        "custom": {"campaign": "q2"},
    }
    assert batch["id"] == "batch_1"


def test_bulk_takes_the_list_positionally(client, api):
    api.add("POST", "/email/verify/bulk", 201, BULK_STARTED)

    client.verify.bulk(EMAILS)

    assert api.calls("POST", "/email/verify/bulk")[0]["json"] == {"verifications": EMAILS}


def test_bulk_emails_is_a_deprecated_alias(client, api):
    api.add("POST", "/email/verify/bulk", 201, BULK_STARTED)

    with pytest.warns(DeprecationWarning):
        client.verify.bulk(emails=EMAILS)

    assert api.calls("POST", "/email/verify/bulk")[0]["json"] == {"verifications": EMAILS}


@pytest.mark.parametrize(
    "kwargs",
    [
        {},
        {"verifications": EMAILS, "emails": EMAILS},
        {"verifications": "pam.beesly@dundermifflin.com"},
    ],
)
def test_bulk_refuses_bad_arguments_before_any_request(client, api, kwargs):
    with pytest.raises(TypeError):
        client.verify.bulk(**kwargs)

    assert api.requests == []


def test_get_bulk_reads_the_batch_id(client, api):
    api.add("GET", "/email/verify/bulk", 200, {"general": {"id": "batch_1", "status": "ongoing"}})

    client.verify.get_bulk("batch_1")

    assert api.calls("GET", "/email/verify/bulk")[0]["params"] == {"id": "batch_1"}


def test_single_and_get(client, api):
    api.add("POST", "/email/verify/single", 200, {
        "message": "Single verification operating",
        "id": "verif_1",
        "credits_used": 0.25,
    })
    api.add("GET", "/email/verify/single", 200, {
        "email": "pam.beesly@dundermifflin.com",
        "qualification": "valid",
    })

    verification = client.verify.single(email="pam.beesly@dundermifflin.com")
    result = client.verify.get(verification["id"])

    assert api.calls("POST", "/email/verify/single")[0]["json"] == {
        "email": "pam.beesly@dundermifflin.com",
    }
    assert api.calls("GET", "/email/verify/single")[0]["params"] == {"id": "verif_1"}
    assert result["qualification"] == "valid"


def test_async_bulk_sends_verifications(api):
    api.add("POST", "/email/verify/bulk", 201, BULK_STARTED)

    async def main():
        async with AsyncEnrow("test_key") as client:
            return await client.verify.bulk(EMAILS)

    batch = asyncio.run(main())

    assert api.calls("POST", "/email/verify/bulk")[0]["json"] == {"verifications": EMAILS}
    assert batch["id"] == "batch_1"


def test_async_bulk_emails_alias(api):
    api.add("POST", "/email/verify/bulk", 201, BULK_STARTED)

    async def main():
        async with AsyncEnrow("test_key") as client:
            return await client.verify.bulk(emails=EMAILS)

    with pytest.warns(DeprecationWarning):
        asyncio.run(main())

    assert api.calls("POST", "/email/verify/bulk")[0]["json"] == {"verifications": EMAILS}
