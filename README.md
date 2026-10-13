# Enrow Python SDK

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/EnrowAPI/enrow-python)](https://github.com/EnrowAPI/enrow-python)
[![Last commit](https://img.shields.io/github/last-commit/EnrowAPI/enrow-python)](https://github.com/EnrowAPI/enrow-python/commits)

Find professional emails and phone numbers, and verify emails, with the [Enrow API](https://enrow.io).

## Install

The SDK is not published on PyPI: install it from this repository.

```bash
pip install git+https://github.com/EnrowAPI/enrow-python.git
```

Python 3.8 or later.

## Quick start

```python
from enrow import Enrow

client = Enrow("your_api_key")

result = client.email.find(
    full_name="Dwight Schrute",
    company_domain="dundermifflin.com",
    wait_for_result=True,
)

print(result["qualification"])  # "valid" (email found) or "invalid"
print(result.get("email"))      # dwight.schrute@dundermifflin.com
```

Every search runs in the background: `find` starts it and returns its `id`, and the result comes from `get(id)`, from `wait_for_result=True`, or from your [webhook](https://docs.enrow.io/how-webhooks-work). Until it is finished, `get` answers `{"qualification": "ongoing"}`.

## Email Finder

```python
# Start a search from a full name and a company (company_domain or company_name)
search = client.email.find(
    full_name="Dwight Schrute",
    company_domain="dundermifflin.com",
    custom={"crm_id": "lead_001"},  # returned as-is with the result
    settings={"webhook": "https://yourapp.com/webhook"},
)
print(search["id"])

# Get the result by its id
result = client.email.get(search["id"])

# Or wait for it: polls every poll_interval seconds, for up to timeout seconds
result = client.email.find(
    full_name="Dwight Schrute",
    company_name="Dunder Mifflin",
    settings={"country_code": "US"},
    retrieve_gender=True,
    wait_for_result=True,
    poll_interval=2,
    timeout=60,
)
if result["qualification"] == "ongoing":
    # Still running after the timeout: the result carries the search id
    result = client.email.get(result["id"])

# Search from a LinkedIn profile URL
result = client.email.find(
    linkedin_url="https://www.linkedin.com/in/dwight-schrute",
    wait_for_result=True,
)
print(result.get("linkedin_status"))  # "found", "email_not_found", "no_current_company"...

# Company information, only effective with the country code FR
search = client.email.find(
    full_name="Dwight Schrute",
    company_name="Dunder Mifflin",
    settings={"country_code": "FR"},
    retrieve_company_info=True,
)

# Bulk search: up to 5,000 searches, with the API field names
batch = client.email.find_bulk(
    searches=[
        {"fullname": "Dwight Schrute", "company_domain": "dundermifflin.com", "custom": "lead_001"},
        {"fullname": "Jim Halpert", "company_name": "Dunder Mifflin", "custom": "lead_002"},
    ],
    settings={"webhook": "https://yourapp.com/webhook"},
)

results = client.email.get_bulk(batch["id"])
if results["general"]["status"] == "completed":
    for row in results["results"]:
        print(row["qualification"], row.get("email"))
```

A search from a LinkedIn profile URL works for single searches only and may not be available on every account: see [Search from a LinkedIn profile URL](https://docs.enrow.io/api-reference/email-finder/find-single#search-from-a-linkedin-profile-url).

## Email Verifier

```python
verification = client.verify.single(email="pam.beesly@dundermifflin.com")

result = client.verify.get(verification["id"])
print(result["qualification"])  # "valid", "invalid", or "ongoing" while it runs

# Bulk: up to 5,000 emails
batch = client.verify.bulk(
    verifications=["pam.beesly@dundermifflin.com", "angela.martin@dundermifflin.com"],
    settings={"webhook": "https://yourapp.com/webhook"},
)
results = client.verify.get_bulk(batch["id"])
```

## Phone Finder

```python
# From a LinkedIn profile URL (recommended)
search = client.phone.find(linkedin_url="https://www.linkedin.com/in/michael-scott/")

# From a first name, a last name and a company (company_domain or company_name)
search = client.phone.find(
    first_name="Michael",
    last_name="Scott",
    company_domain="dundermifflin.com",
)
result = client.phone.get(search["id"])

# Wait for the result
result = client.phone.find(
    linkedin_url="https://www.linkedin.com/in/michael-scott/",
    wait_for_result=True,
)
print(result["qualification"], result.get("number"))  # found +15705551234

# Bulk: up to 3,000 searches, with the API field names
batch = client.phone.find_bulk(
    searches=[
        {"linkedin_url": "https://www.linkedin.com/in/michael-scott/"},
        {"firstname": "Dwight", "lastname": "Schrute", "company_domain": "dundermifflin.com"},
    ],
)
results = client.phone.get_bulk(batch["id"])
```

## Account

```python
info = client.account.info()
print(info["credits"])  # 36000
```

## Async

```python
import asyncio
from enrow import AsyncEnrow


async def main():
    async with AsyncEnrow("your_api_key") as client:
        result = await client.email.find(
            full_name="Dwight Schrute",
            company_domain="dundermifflin.com",
            wait_for_result=True,
        )
        print(result["qualification"])


asyncio.run(main())
```

## Error handling

```python
from enrow import AuthenticationError, EnrowError, InsufficientBalanceError, RateLimitError

try:
    search = client.email.find(full_name="Dwight Schrute", company_domain="dundermifflin.com")
except AuthenticationError:
    pass  # 401: missing or invalid API key
except InsufficientBalanceError:
    pass  # 402: not enough credits
except RateLimitError:
    pass  # 429: more than 10 POST requests per second, retry with backoff
except EnrowError as e:
    print(e.status, e.message)
```

## Credits

| Endpoint | Cost |
|----------|------|
| Email Finder | 1 credit per email found |
| Email Verifier | 0.25 credit per verification |
| Phone Finder | 40 credits per phone found (50 on legacy plans) |

See [Credits & billing](https://docs.enrow.io/credits-billing) for the details.

## Links

- [API Documentation](https://docs.enrow.io)
- [Enrow](https://enrow.io)

## License

MIT
