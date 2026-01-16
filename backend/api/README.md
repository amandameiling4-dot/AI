# Code AI API Server

FastAPI server for code model inference with billing, auth, and usage tracking.

## Setup

```bash
pip install -r requirements-api.txt
pip install -r requirements-train.txt  # (also need transformers, torch, etc)
```

## Running locally

```bash
python -m uvicorn backend.api.server:app --reload --port 8000
```

## API endpoints

- `GET /health` — health check
- `POST /v1/completions` — request code completion (requires Bearer token)
- `GET /v1/account/usage` — get usage stats (requires Bearer token)

## Example

```python
from sdk.python.client import CodeAIClient

client = CodeAIClient(api_key='your-api-key')
result = client.complete(prompt='def add(a, b):', max_tokens=50)
print(result)
```

## Billing integration

Usage is logged per API key. See `backend/billing/` for invoice and subscription handling.

## Future work

- Persistent usage logging to database
- Rate limiting and quota enforcement
- Streaming responses
- Batch completions
- Model selection per request
