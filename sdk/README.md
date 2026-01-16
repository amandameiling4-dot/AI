# SDK for Code AI

Python and JavaScript SDKs for the Code AI API.

## Python SDK

```python
from sdk.python.client import CodeAIClient

client = CodeAIClient(api_key='your-api-key', base_url='https://api.codeai.example.com')

# Get completion
result = client.complete(prompt='def add(a, b):', max_tokens=50)
print(result['completion'])

# Check usage
usage = client.get_usage()
print(f"Used {usage['tokens_used_this_month']} tokens")
```

## JavaScript SDK (future)

Coming soon: TypeScript/JavaScript client for Node.js and browsers.

See `backend/api/README.md` for API docs.
