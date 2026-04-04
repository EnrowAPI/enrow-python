# Enrow Python SDK

Find and verify professional emails, phone numbers, and contact information with the [Enrow API](https://enrow.io).

## Install

```bash
pip install enrow
```

## Quick start

```python
from enrow import Enrow

client = Enrow("your_api_key")

result = client.email.find(
    company_domain="apple.com",
    full_name="Tim Cook",
)

print(result["email"])  # tcook@apple.com
```

## Email Finder

```python
# Find a single email
search = client.email.find(
    company_domain="apple.com",
    full_name="Tim Cook",
    settings={"country_code": "US"},
)

# Wait for result (auto-polling)
result = client.email.find(
    company_domain="apple.com",
    full_name="Tim Cook",
    wait_for_result=True,
)

# Get result by ID
result = client.email.get("search_abc123")

# Bulk search
batch = client.email.find_bulk(
    searches=[
        {"company_domain": "apple.com", "fullname": "Tim Cook"},
        {"company_domain": "microsoft.com", "fullname": "Satya Nadella"},
    ],
    settings={"webhook": "https://yourapp.com/webhook"},
)

results = client.email.get_bulk(batch["batch_id"])
```

## Email Verifier

```python
verification = client.verify.single(email="tcook@apple.com")
print(verification["qualification"])  # "valid"

# Bulk
batch = client.verify.bulk(emails=["a@b.com", "c@d.com"])
results = client.verify.get_bulk(batch["batch_id"])
```

## Phone Finder

```python
# By LinkedIn URL
phone = client.phone.find(linkedin_url="https://linkedin.com/in/timcook")

# By name + company
phone = client.phone.find(
    first_name="Tim",
    last_name="Cook",
    company_domain="apple.com",
)

# Wait for result
result = client.phone.find(
    linkedin_url="https://linkedin.com/in/timcook",
    wait_for_result=True,
)
```

## Reverse Email

```python
person = client.reverse_email.find(email="tcook@apple.com")
print(person["first_name"])  # "Tim"
print(person["linkedin_url"])

# Bulk
batch = client.reverse_email.find_bulk(
    emails=[{"email": "tcook@apple.com"}, {"email": "snadella@microsoft.com"}]
)
results = client.reverse_email.get_bulk(batch["id"])
```

## Account

```python
info = client.account.info()
print(info["credits"])  # 8500
```

## Async

```python
from enrow import AsyncEnrow

async with AsyncEnrow("your_api_key") as client:
    result = await client.email.find(
        company_domain="apple.com",
        full_name="Tim Cook",
    )
```

## Error handling

```python
from enrow import Enrow, RateLimitError, InsufficientBalanceError, EnrowError

try:
    result = client.email.find(company_domain="apple.com", full_name="Tim Cook")
except RateLimitError:
    pass  # 429
except InsufficientBalanceError:
    pass  # 402
except EnrowError as e:
    print(e.status, e.message)
```

## Credits

| Endpoint | Cost |
|----------|------|
| Email Finder | 1 credit/email |
| Email Verifier | 0.25 credit/email |
| Phone Finder | 50 credits/phone |
| Reverse Email | 5 credits/lookup |

## Links

- [API Documentation](https://docs.enrow.io)
- [Enrow](https://enrow.io)

## License

MIT
