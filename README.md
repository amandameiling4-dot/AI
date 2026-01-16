# CodeAI - Production-Ready Code Completion Platform

A comprehensive, open-source AI coding assistant platform with billing, evaluation, monitoring, and legal compliance built in. Get started in 5 minutes with the quick-start guide below.

**Status**: ✅ MVP Complete — Ready for beta testing and production deployment

---

## 🚀 Quick Start

Get up and running in 5 minutes:

```bash
# 1. Clone and setup
git clone https://github.com/yourusername/CodeAI.git
cd CodeAI
python3 -m venv venv && source venv/bin/activate

# 2. Install & configure
pip install -r requirements-api.txt
cp .env.example .env  # Configure API key, Stripe, database

# 3. Start the API server
python -m uvicorn backend.api.server:app --reload --port 8000

# 4. Make your first completion
curl -X POST http://localhost:8000/v1/completions \
  -H "Authorization: Bearer test_key_12345" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "def fibonacci(", "max_tokens": 50}'
```

**Full quick-start guide**: See [QUICKSTART.md](QUICKSTART.md)

---

## 📚 Documentation

### Getting Started
- **[QUICKSTART.md](QUICKSTART.md)** — 5-minute setup for developers
- **[API.md](API.md)** — Complete API reference with curl examples
- **[DEPLOY.md](DEPLOY.md)** — Production deployment (Docker, Kubernetes, AWS)
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** — File tree and architecture

### Technical Docs
- **[docs/MVP_SPEC.md](docs/MVP_SPEC.md)** — MVP specification and success metrics
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — System architecture and deployment
- **[docs/MODEL_CHOICES.md](docs/MODEL_CHOICES.md)** — Model selection (StarCoder-7B)
- **[docs/BILLING.md](docs/BILLING.md)** — Stripe billing and usage metering

### Data & Training
- **[docs/DATA_MANIFEST.md](docs/DATA_MANIFEST.md)** — Dataset sources and licensing
- **[scripts/data/README.md](scripts/data/README.md)** — Data pipeline (scrub, dedupe, ingest)
- **[scripts/train/README.md](scripts/train/README.md)** — PEFT/LoRA fine-tuning
- **[scripts/eval/README.md](scripts/eval/README.md)** — Evaluation and benchmarks

### Compliance & Security
- **[docs/PRIVACY.md](docs/PRIVACY.md)** — Privacy policy (GDPR/CCPA compliant)
- **[docs/TERMS.md](docs/TERMS.md)** — Terms of service and liability
- **[docs/DATA_COMPLIANCE.md](docs/DATA_COMPLIANCE.md)** — Compliance (SOC 2, encryption, access control)
- **[docs/SECURITY.md](docs/SECURITY.md)** — Security policies and bug bounty program
- **[docs/ACCEPTABLE_USE.md](docs/ACCEPTABLE_USE.md)** — Prohibited uses and enforcement

### Release & Operations
- **[RELEASE.md](RELEASE.md)** — Release checklist and procedures
- **[backend/monitoring/README.md](backend/monitoring/README.md)** — Monitoring and observability

---

## 🛠️ Components

### Data Pipeline
```bash
cd scripts/data
python run_pipeline.py  # Ingest → Scrub secrets/PII → Deduplicate
```
- **scrub_secrets.py** — Removes AWS keys, JWT, CC#, email, phone, SSN
- **pii_detector.py** — Optional spaCy-based PII detection
- **deduplicate.py** — SHA256-based duplicate detection

### Training & Inference
```bash
cd scripts/train
python train_peft.py --model starcode-7b --dataset your_data.jsonl
python infer.py --prompt "def fibonacci(" --max_tokens 50
```

### Evaluation & Benchmarks
```bash
cd scripts/eval
python run_benchmarks.py --output results.json  # HumanEval + performance
```

### API Server
```bash
cd backend/api
python -m uvicorn server:app --port 8000
```
- `/health` — Server health check
- `/v1/completions` — Generate code completion
- `/v1/account/usage` — Check token usage and billing
- `/billing/subscribe` — Stripe checkout
- `/metrics` — Prometheus metrics

### Python SDK
```python
from sdk.python.client import CodeAIClient

client = CodeAIClient(api_key="sk_test_...", base_url="http://localhost:8000")
response = client.complete(prompt="def hello(", max_tokens=30)
print(response['completion'])  # Generated code
```

### VS Code Extension
```bash
cd extensions/vscode
npm install && npm run compile
# In VS Code: Press Ctrl+Shift+P → "CodeAI: Set API Key"
```

---

## 📊 Benchmarks & Metrics

**Performance Baselines** (on dummy task):
- **Throughput**: 90.62 req/sec
- **Latency**: 11.02ms avg, 13.07ms p95
- **Memory**: ~2GB for StarCoder-7B (with quantization: ~1GB)

**Code Quality Evaluation**:
- HumanEval integration with pass@k computation
- Code style heuristics (naming, indentation, complexity)
- Exact and soft-match evaluation modes

Run benchmarks:
```bash
python scripts/eval/run_benchmarks.py --output bench_results.json
```

---

## 💳 Billing

**Pricing Tiers**:
| Tier | Requests/Min | Tokens/Month | Price |
|------|--------------|--------------|-------|
| Free | 10 | 10,000 | $0 |
| Starter | 100 | 100,000 | $20/mo |
| Pro | 600 | 1,000,000 | $99/mo |
| Enterprise | Custom | Custom | Contact sales |

**Stripe Integration**:
- Usage metering: Tokens tracked and billed
- Webhook support: invoice.paid, payment_failed, checkout.completed
- Rate limiting: Enforced per tier with 429 response

See [docs/BILLING.md](docs/BILLING.md) for setup.

---

## 🔐 Security & Compliance

- **Privacy**: GDPR/CCPA compliant data retention (30d code, 12mo metrics, 7y billing)
- **Encryption**: TLS for all APIs, AES-256 for data at rest
- **Monitoring**: Prometheus metrics, JSONL audit logs, FastAPI middleware auto-instrumentation
- **Bug Bounty**: $100–$10k for security research
- **SOC 2 Roadmap**: Access control, incident response, vendor audits

See [docs/SECURITY.md](docs/SECURITY.md) and [docs/PRIVACY.md](docs/PRIVACY.md).

---

## 🚢 Deployment

**Local Development**:
```bash
docker-compose up -d  # API, PostgreSQL, Prometheus, Kibana
```

**Production**:
- **Docker**: Single container ~2GB with model
- **Kubernetes**: Helm chart with HPA, Ingress, service mesh
- **AWS**: ECS Fargate or EC2 with Auto Scaling, RDS, CloudWatch

See [DEPLOY.md](DEPLOY.md) for full deployment guide.

---

## 📦 Project Structure

```
CodeAI/
├── QUICKSTART.md, API.md, DEPLOY.md, RELEASE.md
├── docs/                          # Compliance, architecture, billing
├── scripts/data/                  # Data pipeline (scrub, dedupe, ingest)
├── scripts/train/                 # PEFT fine-tuning and inference
├── scripts/eval/                  # Benchmarks and evaluation
├── backend/api/                   # FastAPI server
├── backend/billing/               # Stripe integration
├── backend/monitoring/            # Prometheus, logging, metrics
├── sdk/python/                    # Python client library
├── extensions/vscode/             # VS Code extension
├── examples/                      # Code examples
├── tests/                         # Unit and integration tests
└── docker-compose.yml             # Local dev environment
```

Full tree: See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

---

## 🧪 Examples

### Python SDK
```python
from sdk.python.client import CodeAIClient

client = CodeAIClient(api_key="test_key_12345")

# Generate completion
response = client.complete(
    prompt="def fibonacci(n):",
    max_tokens=50,
    temperature=0.7
)
print(response['completion'])

# Check usage
usage = client.get_usage()
print(f"Tokens used: {usage['total_tokens']}")
```

### curl & Shell
```bash
curl -X POST http://localhost:8000/v1/completions \
  -H "Authorization: Bearer test_key_12345" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "def sum_list(", "max_tokens": 30}'
```

See [examples/](examples/) for more.

---

## 🤝 Contributing

We welcome contributions! Please see the project board and open issues for areas to help.

**Development Setup**:
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements-dev.txt
pytest tests/  # Run tests
```

---

## 📜 License

This project is licensed under [LICENSE](LICENSE).

---

## 📞 Support

- **Docs**: https://codeai.example.com/docs
- **Issues**: [GitHub Issues](https://github.com/yourusername/CodeAI/issues)
- **Email**: support@codeai.example.com
- **Status**: [Status Page](https://status.codeai.example.com)

---

## 🎯 Roadmap

- ✅ MVP: API, SDK, billing, monitoring, compliance
- ⏳ Beta: Jupyter examples, GitHub Copilot plugin, JetBrains plugin
- 🚀 v1.0: Enterprise features (SSO, audit logs, custom models, SLA)

---

**CodeAI** — *Every app deserves great code completion.* 🎉

## Quick API usage

```python
from sdk.python.client import CodeAIClient

client = CodeAIClient(api_key='your-key')
result = client.complete(prompt='def add(a, b):', max_tokens=50)
print(result['completion'])
```

Start the API server:
```bash
python -m uvicorn backend.api.server:app --reload --port 8000
```

## VS Code extension

Install and configure:
```bash
cd extensions/vscode && npm install && npm run compile
# In VS Code: set codeAI.apiKey and codeAI.apiEndpoint in settings
```


## Development

- Quick setup (create a virtualenv first is recommended):

```bash
make setup
```

- Run tests:

```bash
make test
```

- Run the sample data pipeline locally:

```bash
make run-pipeline
```

CI: GitHub Actions runs `pytest` and the sample data pipeline on PRs and uses a pip cache for faster installs (see `.github/workflows/data-pipeline.yml`).