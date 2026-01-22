# CodeAI Quick Start Guide

Get up and running with CodeAI in 5 minutes.

## Prerequisites

- Python 3.10+
- Git
- (Optional) VS Code for editor integration

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/CodeAI.git
cd CodeAI
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-api.txt
pip install -r requirements-monitoring.txt
```

### 3. Configure Environment

```bash
cp .env.example .env

# Edit .env with your settings:
# STRIPE_API_KEY=sk_test_...
# DATABASE_URL=sqlite:///codeai.db
# MODEL_PATH=/path/to/starcode-7b
```

## Run the API Server

```bash
cd backend/api
python -m uvicorn server:app --reload --port 8000
```

Server starts at `http://localhost:8000`

**Health check:**
```bash
curl http://localhost:8000/health
# Expected: {"status": "ok"}
```

## Get an API Key

```bash
# Via Stripe billing endpoint
curl -X POST http://localhost:8000/billing/subscribe \
  -H "Content-Type: application/json" \
  -d '{"price_id": "price_1234567890", "customer_email": "user@example.com"}'

# Or for local testing, generate a test token:
# See backend/api/server.py - hardcoded test key: "test_key_12345"
```

## Make Your First Completion Request

```bash
curl -X POST http://localhost:8000/v1/completions \
  -H "Authorization: Bearer test_key_12345" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "def fibonacci(",
    "max_tokens": 50,
    "temperature": 0.7
  }'

# Expected response:
# {
#   "completion": "n):\n    if n <= 1:\n        return n\n    else:\n        return fibonacci(n-1) + fibonacci(n-2)",
#   "tokens_used": 28,
#   "latency_ms": 145.3
# }
```

## Use the Python SDK

```python
from sdk.python.client import CodeAIClient

# Initialize client
client = CodeAIClient(
    api_key="test_key_12345",
    base_url="http://localhost:8000"
)

# Get completion
response = client.complete(
    prompt="def hello_world(",
    max_tokens=30,
    temperature=0.5
)

print(response['completion'])

# Check usage
usage = client.get_usage()
print(f"Tokens used: {usage['total_tokens']}")

# Check server health
health = client.health()
print(f"Server status: {health['status']}")
```

## Set Up VS Code Extension (Optional)

### Local Development Setup

```bash
cd extensions/vscode

# Install dependencies
npm install

# Compile TypeScript
npm run compile

# Or run in watch mode for development:
npm run watch
```

### Load Extension into VS Code

1. Open VS Code
2. Press `Ctrl+Shift+D` (Debug)
3. Click "Run Extension"
4. A new VS Code window opens with the extension loaded

### Configure API Key

1. In the extension VS Code window, press `Ctrl+Shift+P`
2. Run: **CodeAI: Set API Key**
3. Enter your API key (or `test_key_12345`)
4. Configure endpoint if not using `http://localhost:8000`

### Test Inline Completions

1. Create a new Python file (`.py`)
2. Type a function definition: `def fibonacci(n):`
3. Press the CodeAI completion hotkey or wait for inline suggestions
4. Extension will fetch and display completions from your API

## Run Benchmarks

```bash
cd scripts/eval

# Run all benchmarks
python run_benchmarks.py --output results.json

# Run individual benchmark suites
python performance.py                     # Latency & throughput
python evaluate.py --mode quality         # Code quality metrics
python humaneval.py --num_problems 10     # HumanEval subset
```

## Next Steps

- **Read the full API docs:** See [API.md](API.md) for endpoint reference
- **Deploy to production:** See [DEPLOY.md](DEPLOY.md) for Docker & Kubernetes guides
- **Configure billing:** See [docs/BILLING.md](docs/BILLING.md) for Stripe setup
- **Review compliance:** See [docs/PRIVACY.md](docs/PRIVACY.md) and [docs/TERMS.md](docs/TERMS.md)
- **Monitor in production:** See [backend/monitoring/README.md](backend/monitoring/README.md) for Prometheus setup

## Troubleshooting

### Port 8000 already in use

```bash
# Use a different port
python -m uvicorn server:app --port 8001
```

### ModuleNotFoundError importing sdk

```bash
# Add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/workspaces/AI"
python your_script.py
```

### Stripe webhook events not triggering

1. Start the Stripe CLI forwarder (see [backend/billing/README.md](backend/billing/README.md))
2. Verify your endpoint URL in `.env`
3. Check logs at `backend/logs/`

### Extension not showing completions

1. Verify API key is set: **CodeAI: Get Usage**
2. Check API endpoint is reachable: `curl http://localhost:8000/health`
3. Check browser console: `Ctrl+Shift+I` in extension VS Code window

## Support

- **Issues:** Open a GitHub issue
- **Docs:** Full documentation in [docs/](docs/) folder
- **Examples:** Code examples in [examples/](examples/) folder
