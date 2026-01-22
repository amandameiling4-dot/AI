# CodeAI API Reference

Complete reference for the CodeAI inference API.

## Base URL

```
http://localhost:8000  (development)
https://api.codeai.example.com  (production)
```

## Authentication

All API requests require Bearer token authentication in the `Authorization` header:

```bash
Authorization: Bearer YOUR_API_KEY
```

**Obtaining an API key:**
```bash
curl -X POST https://api.codeai.example.com/billing/subscribe \
  -H "Content-Type: application/json" \
  -d '{"price_id": "price_1234567890", "customer_email": "user@example.com"}'
```

Response includes `checkout_url` to complete payment and receive API key.

---

## Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

**Authentication:** Not required

**Description:** Check if the API server is running.

**Example:**
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "ok",
  "model_loaded": false
}
```

**Status Codes:**
- `200 OK` - Server is healthy

---

### 2. Generate Code Completion

**Endpoint:** `POST /v1/completions`

**Authentication:** Required (Bearer token)

**Description:** Generate code completions based on a prompt.

**Request Headers:**
```
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

**Request Body:**
```json
{
  "prompt": "def fibonacci(",
  "max_tokens": 50,
  "temperature": 0.7,
  "top_p": 0.95,
  "stop": ["\n\n", "def "]
}
```

**Request Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | string | Required | The code prompt to complete |
| `max_tokens` | integer | 50 | Maximum tokens to generate (1-512) |
| `temperature` | float | 0.7 | Sampling temperature (0.0-2.0), higher = more creative |
| `top_p` | float | 0.95 | Nucleus sampling parameter (0.0-1.0) |
| `stop` | array | [] | Stop sequences to terminate generation |

**Example:**
```bash
curl -X POST http://localhost:8000/v1/completions \
  -H "Authorization: Bearer test_key_12345" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "def fibonacci(",
    "max_tokens": 50,
    "temperature": 0.7
  }'
```

**Response:**
```json
{
  "prompt": "def fibonacci(",
  "completion": "n):\n    if n <= 1:\n        return n\n    else:\n        return fibonacci(n-1) + fibonacci(n-2)",
  "tokens_used": 28,
  "latency_ms": 145.3,
  "stop_reason": "length"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `prompt` | string | The original prompt that was submitted |
| `completion` | string | The generated code completion |
| `tokens_used` | integer | Number of tokens consumed |
| `latency_ms` | float | API response time in milliseconds |
| `stop_reason` | string | Why generation stopped: `"length"`, `"stop_token"`, or `"eos"` |

**Status Codes:**
- `200 OK` - Successful completion
- `400 Bad Request` - Invalid parameters
- `401 Unauthorized` - Missing or invalid API key
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

**Error Response Example:**
```json
{
  "detail": "Rate limit exceeded. Maximum 100 requests per minute."
}
```

---

### 3. Get Account Usage

**Endpoint:** `GET /v1/account/usage`

**Authentication:** Required (Bearer token)

**Description:** Get token usage and billing information for your account.

**Example:**
```bash
curl -H "Authorization: Bearer test_key_12345" \
  http://localhost:8000/v1/account/usage
```

**Response:**
```json
{
  "api_key": "test_key_12345",
  "total_requests": 1250,
  "total_tokens": 125432,
  "total_cost_cents": 625,
  "requests_this_month": 890,
  "tokens_this_month": 98750,
  "cost_this_month_cents": 493,
  "subscription_tier": "pro",
  "rate_limit_rpm": 600,
  "requests_remaining_this_minute": 599
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `api_key` | string | Your API key (last 6 chars visible) |
| `total_requests` | integer | Total requests since account creation |
| `total_tokens` | integer | Total tokens consumed |
| `total_cost_cents` | integer | Total cost in cents ($) |
| `requests_this_month` | integer | Requests in current billing month |
| `tokens_this_month` | integer | Tokens consumed this month |
| `cost_this_month_cents` | integer | Cost this month in cents |
| `subscription_tier` | string | `"free"`, `"starter"`, `"pro"`, or `"enterprise"` |
| `rate_limit_rpm` | integer | Maximum requests per minute |
| `requests_remaining_this_minute` | integer | Remaining requests before rate limit |

**Status Codes:**
- `200 OK` - Successful
- `401 Unauthorized` - Invalid API key
- `404 Not Found` - Account not found

---

### 4. Subscribe / Create Billing Account

**Endpoint:** `POST /billing/subscribe`

**Authentication:** Not required

**Description:** Create a billing account and generate an API key via Stripe Checkout.

**Request Body:**
```json
{
  "price_id": "price_1234567890",
  "customer_email": "user@example.com"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/billing/subscribe \
  -H "Content-Type: application/json" \
  -d '{"price_id": "price_1234567890", "customer_email": "user@example.com"}'
```

**Response:**
```json
{
  "checkout_url": "https://checkout.stripe.com/pay/cs_live_...",
  "session_id": "cs_live_123abc"
}
```

Redirect user to `checkout_url` to complete signup and payment. After completion, user receives API key via email.

**Status Codes:**
- `200 OK` - Checkout session created
- `400 Bad Request` - Invalid email
- `500 Internal Server Error` - Stripe API error

---

### 5. Record Usage (Webhooks)

**Endpoint:** `POST /billing/usage`

**Authentication:** Required (Bearer token)

**Description:** (Usually automatic) Record a usage event for billing.

**Request Body:**
```json
{
  "tokens": 150,
  "latency_ms": 245.5
}
```

**Status Codes:**
- `200 OK` - Usage recorded
- `401 Unauthorized` - Invalid API key

---

### 6. Stripe Webhook Handler

**Endpoint:** `POST /billing/webhook`

**Authentication:** Stripe signature verification

**Description:** Receive Stripe events for billing updates.

**Expected Events:**
- `invoice.paid` - Invoice paid successfully
- `invoice.payment_failed` - Payment failed
- `checkout.session.completed` - User completed Stripe Checkout

**Setup:**

```bash
# Using Stripe CLI (development)
stripe listen --forward-to localhost:8000/billing/webhook

# Configure webhook secret in .env:
STRIPE_WEBHOOK_SECRET=whsec_test_...
```

---

## Rate Limiting

API requests are rate-limited based on subscription tier:

| Tier | Requests/Min | Tokens/Month | Cost |
|------|--------------|--------------|------|
| Free | 10 | 10,000 | $0 |
| Starter | 100 | 100,000 | $20/mo |
| Pro | 600 | 1,000,000 | $99/mo |
| Enterprise | Custom | Custom | Contact sales |

**Rate Limit Headers:**
```
X-RateLimit-Limit: 600
X-RateLimit-Remaining: 599
X-RateLimit-Reset: 1705419600
```

When rate limit exceeded, API returns `429 Too Many Requests`.

---

## Error Handling

All errors return JSON with status code and error detail:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common Error Cases:**

| Status | Error | Solution |
|--------|-------|----------|
| 400 | "Invalid max_tokens: must be 1-512" | Adjust max_tokens parameter |
| 401 | "Missing API key" | Add Authorization header with Bearer token |
| 401 | "Invalid API key format" | Ensure Authorization header starts with "Bearer " |
| 429 | "Rate limit exceeded" | Wait before retrying or upgrade tier |
| 500 | "Internal server error" | Retry with exponential backoff |

---

## Python SDK

The Python SDK provides a simpler interface:

```python
from sdk.python.client import CodeAIClient

client = CodeAIClient(
    api_key="your_api_key",
    base_url="http://localhost:8000"
)

# Generate completion
response = client.complete(
    prompt="def hello(",
    max_tokens=30,
    temperature=0.5
)
print(response['completion'])

# Get usage
usage = client.get_usage()
print(f"Total tokens: {usage['total_tokens']}")

# Check health
health = client.health()
print(f"Status: {health['status']}")
```

---

## Curl Examples

### Generate a completion
```bash
curl -X POST http://localhost:8000/v1/completions \
  -H "Authorization: Bearer test_key_12345" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "def sum_list(numbers):",
    "max_tokens": 50,
    "temperature": 0.7
  }' | jq .
```

### Get usage and check remaining quota
```bash
curl -H "Authorization: Bearer test_key_12345" \
  http://localhost:8000/v1/account/usage | jq '.cost_this_month_cents, .requests_remaining_this_minute'
```

### Create a subscription
```bash
curl -X POST http://localhost:8000/billing/subscribe \
  -H "Content-Type: application/json" \
  -d '{"price_id": "price_1234567890", "customer_email": "newuser@example.com"}' | jq '.checkout_url'
```

---

## Versioning

Current API version: **v1**

Future versions will be accessible at:
- `/v2/completions`
- `/v3/completions`

Deprecated versions will receive 12 months of support.

---

## Support & Feedback

- **Issues:** https://github.com/yourusername/CodeAI/issues
- **Email:** support@codeai.example.com
- **Docs:** https://codeai.example.com/docs
