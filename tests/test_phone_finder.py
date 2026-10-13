import asyncio

from enrow import AsyncEnrow

SEARCH_STARTED = {
    "credits_used": 40,
    "id": "phone_1",
    "message": "Single search operating",
}


def test_find_by_name_sends_firstname_and_lastname(client, api):
    api.add("POST", "/phone/single", 201, SEARCH_STARTED)

    search = client.phone.find(
        first_name="Michael",
        last_name="Scott",
        company_domain="dundermifflin.com",
        custom="crm_42",
        settings={"webhook": "https://example.com/hook"},
    )

    assert api.calls("POST", "/phone/single")[0]["json"] == {
        "firstname": "Michael",
        "lastname": "Scott",
        "company_domain": "dundermifflin.com",
        "custom": "crm_42",
        "settings": {"webhook": "https://example.com/hook"},
    }
    assert search["id"] == "phone_1"


def test_find_by_linkedin_url(client, api):
    api.add("POST", "/phone/single", 201, SEARCH_STARTED)

    client.phone.find(linkedin_url="https://www.linkedin.com/in/michael-scott/")

    assert api.calls("POST", "/phone/single")[0]["json"] == {
        "linkedin_url": "https://www.linkedin.com/in/michael-scott/",
    }


def test_find_wait_for_result_polls_until_final(client, api):
    api.add("POST", "/phone/single", 201, SEARCH_STARTED)
    api.add("GET", "/phone/single", 202, {"qualification": "ongoing"})
    api.add("GET", "/phone/single", 200, {
        "params": {"linkedin_url": "https://www.linkedin.com/in/michael-scott/"},
        "number": "+15705551234",
        "country": "US",
        "qualification": "found",
    })

    result = client.phone.find(
        linkedin_url="https://www.linkedin.com/in/michael-scott/",
        wait_for_result=True,
        poll_interval=0.001,
    )

    gets = api.calls("GET", "/phone/single")
    assert len(gets) == 2
    assert all(r["params"] == {"id": "phone_1"} for r in gets)
    assert result["id"] == "phone_1"
    assert result["qualification"] == "found"
    assert result["number"] == "+15705551234"


def test_find_bulk_and_get_bulk(client, api):
    api.add("POST", "/phone/bulk", 201, {
        "credits_used": 80,
        "estimated_duration": 1,
        "id": "batch_1",
        "message": "Bulk search operating",
    })
    api.add("GET", "/phone/bulk", 200, {"general": {"id": "batch_1", "status": "ongoing"}})
    searches = [
        {"linkedin_url": "https://www.linkedin.com/in/michael-scott/"},
        {"firstname": "Dwight", "lastname": "Schrute", "company_domain": "dundermifflin.com"},
    ]

    batch = client.phone.find_bulk(searches, custom={"campaign": "q2"})
    client.phone.get_bulk(batch["id"])

    assert api.calls("POST", "/phone/bulk")[0]["json"] == {
        "searches": searches,
        "custom": {"campaign": "q2"},
    }
    assert api.calls("GET", "/phone/bulk")[0]["params"] == {"id": "batch_1"}


def test_async_find_by_name_sends_firstname_and_lastname(api):
    api.add("POST", "/phone/single", 201, SEARCH_STARTED)
    api.add("GET", "/phone/single", 200, {"qualification": "not_found"})

    async def main():
        async with AsyncEnrow("test_key") as client:
            return await client.phone.find(
                first_name="Michael",
                last_name="Scott",
                company_name="Dunder Mifflin",
                wait_for_result=True,
                poll_interval=0.001,
            )

    result = asyncio.run(main())

    assert api.calls("POST", "/phone/single")[0]["json"] == {
        "firstname": "Michael",
        "lastname": "Scott",
        "company_name": "Dunder Mifflin",
    }
    assert result == {"id": "phone_1", "qualification": "not_found"}
