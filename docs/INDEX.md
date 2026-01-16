# CodeAI Documentation Index

Complete reference guide for all CodeAI documentation and resources.

## 🚀 Getting Started (Start Here!)

| Document | Purpose | Read Time |
|----------|---------|-----------|
| [README.md](../README.md) | Project overview and feature summary | 5 min |
| [QUICKSTART.md](../QUICKSTART.md) | 5-minute setup and first API call | 5 min |
| [RELEASE_SUMMARY.md](../RELEASE_SUMMARY.md) | MVP completion summary and achievements | 10 min |

## 📚 API & SDK Documentation

| Document | Purpose | Audience |
|----------|---------|----------|
| [API.md](../API.md) | Complete API reference with endpoints, auth, examples | Developers, integrators |
| [sdk/python/README.md](../sdk/python/README.md) | Python SDK setup and usage | Python developers |
| [examples/python_sdk_example.py](../examples/python_sdk_example.py) | Python SDK code examples | Developers |
| [examples/shell_script_example.sh](../examples/shell_script_example.sh) | Curl and bash examples | DevOps, shell users |

## 🛠️ Infrastructure & Deployment

| Document | Purpose | Audience |
|----------|---------|----------|
| [DEPLOY.md](../DEPLOY.md) | Docker, Kubernetes, AWS deployment | DevOps, SREs |
| [RELEASE.md](../RELEASE.md) | Release procedures, version control, rollback | Release managers |
| [docker-compose.yml](../docker-compose.yml) | Local development stack | Developers |
| [backend/api/README.md](../backend/api/README.md) | API server setup | Backend developers |
| [backend/billing/README.md](../backend/billing/README.md) | Stripe webhook setup | DevOps, backend devs |
| [backend/monitoring/README.md](../backend/monitoring/README.md) | Prometheus and logging setup | DevOps, SREs |

## 🔧 Development Guides

### Data Pipeline
| Document | Purpose |
|----------|---------|
| [scripts/data/README.md](../scripts/data/README.md) | Data scrubbing, deduplication, ingestion |
| [docs/DATA_MANIFEST.md](../docs/DATA_MANIFEST.md) | Dataset sources and licensing |
| [docs/DATA_COMPLIANCE.md](../docs/DATA_COMPLIANCE.md) | Data retention policies |

### Model Training
| Document | Purpose |
|----------|---------|
| [scripts/train/README.md](../scripts/train/README.md) | PEFT/LoRA fine-tuning |
| [docs/MODEL_CHOICES.md](../docs/MODEL_CHOICES.md) | Model selection rationale |

### Evaluation & Benchmarks
| Document | Purpose |
|----------|---------|
| [scripts/eval/README.md](../scripts/eval/README.md) | HumanEval, performance, code quality |

### VS Code Extension
| Document | Purpose |
|----------|---------|
| [extensions/vscode/README.md](../extensions/vscode/README.md) | Extension development setup |

## 📋 Legal & Compliance

| Document | Purpose | Compliance Framework |
|----------|---------|----------------------|
| [docs/PRIVACY.md](../docs/PRIVACY.md) | Privacy policy and user rights | GDPR, CCPA |
| [docs/TERMS.md](../docs/TERMS.md) | Terms of service and liability | Contract law |
| [docs/SECURITY.md](../docs/SECURITY.md) | Security policies and bug bounty | Information security |
| [docs/DATA_COMPLIANCE.md](../docs/DATA_COMPLIANCE.md) | Compliance frameworks and controls | SOC 2, ISO 27001 |
| [docs/ACCEPTABLE_USE.md](../docs/ACCEPTABLE_USE.md) | Acceptable use and enforcement | Conduct policy |

## 🏗️ Architecture & Design

| Document | Purpose |
|----------|---------|
| [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) | System design and deployment options |
| [docs/MVP_SPEC.md](../docs/MVP_SPEC.md) | Original MVP specification |
| [docs/BILLING.md](../docs/BILLING.md) | Billing system design |
| [PROJECT_STRUCTURE.md](../PROJECT_STRUCTURE.md) | Complete file tree and component overview |

## 🧪 Testing & Quality Assurance

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v --cov

# Run specific test file
pytest tests/test_api.py -v

# Generate coverage report
pytest tests/ --cov --cov-report=html
# Open htmlcov/index.html in browser
```

### Running Benchmarks
```bash
cd scripts/eval

# Run all benchmarks
python run_benchmarks.py --output results.json

# Run specific benchmark
python performance.py
python humaneval.py --num_problems 50
```

## 🚢 Deployment Paths

### Local Development
```bash
docker-compose up -d
```
See: [QUICKSTART.md](../QUICKSTART.md)

### Docker Single Container
```bash
docker build -t codeai:latest .
docker run -p 8000:8000 codeai:latest
```
See: [DEPLOY.md](../DEPLOY.md) → Docker Deployment

### Kubernetes
```bash
kubectl create namespace codeai
helm install codeai helm/codeai/ -n codeai
```
See: [DEPLOY.md](../DEPLOY.md) → Kubernetes Deployment

### AWS ECS Fargate
```bash
aws ecs create-cluster --cluster-name codeai-prod
aws ecs register-task-definition --cli-input-json file://task-definition.json
aws ecs create-service --cluster codeai-prod ...
```
See: [DEPLOY.md](../DEPLOY.md) → AWS Deployment

## 🔐 Security Checklist

Before deploying to production:

- [ ] Read [docs/SECURITY.md](../docs/SECURITY.md)
- [ ] Review [docs/DATA_COMPLIANCE.md](../docs/DATA_COMPLIANCE.md)
- [ ] Configure TLS certificates
- [ ] Set up monitoring and alerting
- [ ] Enable rate limiting (see API.md)
- [ ] Rotate secrets (Stripe, database passwords)
- [ ] Enable database backups
- [ ] Test disaster recovery procedures

## 📊 Monitoring & Observability

### Prometheus Metrics
- **Endpoint**: `http://localhost:8000/metrics`
- **Dashboard**: `http://localhost:9090` (in docker-compose)
- **Key Metrics**: Request count, latency percentiles, error rate

### Logs
- **Location**: `backend/logs/` (local) or CloudWatch (AWS)
- **Format**: JSONL with structured fields (timestamp, user, tokens, latency)

### Real-Time Monitoring
```bash
# Watch API logs
kubectl logs -f deployment/codeai -n codeai

# Check metrics
curl http://localhost:8000/metrics | grep inference
```

See: [backend/monitoring/README.md](../backend/monitoring/README.md)

## 📞 Support & Help

| Resource | Purpose |
|----------|---------|
| [README.md](../README.md) | General overview and quick answers |
| [QUICKSTART.md](../QUICKSTART.md) | Setup issues and first steps |
| [API.md](../API.md) | API usage questions and error codes |
| [DEPLOY.md](../DEPLOY.md) | Deployment and operational issues |
| [RELEASE.md](../RELEASE.md) | Release procedures and hotfixes |
| GitHub Issues | Bug reports and feature requests |
| Email: support@codeai.example.com | Commercial support |

## 🎯 Common Tasks

### "I want to get started immediately"
→ Read [QUICKSTART.md](../QUICKSTART.md)

### "I need to integrate CodeAI into my app"
→ Read [API.md](../API.md) and [sdk/python/README.md](../sdk/python/README.md)

### "I want to deploy to production"
→ Read [DEPLOY.md](../DEPLOY.md) and [RELEASE.md](../RELEASE.md)

### "I need to fine-tune the model"
→ Read [scripts/train/README.md](../scripts/train/README.md)

### "I want to understand the architecture"
→ Read [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) and [PROJECT_STRUCTURE.md](../PROJECT_STRUCTURE.md)

### "I need to monitor the system"
→ Read [backend/monitoring/README.md](../backend/monitoring/README.md)

### "I need to handle legal/compliance"
→ Read [docs/PRIVACY.md](../docs/PRIVACY.md) and [docs/SECURITY.md](../docs/SECURITY.md)

## 📈 Document Statistics

| Category | Count | Pages |
|----------|-------|-------|
| Getting Started | 3 | 25 |
| API & SDK | 4 | 30 |
| Infrastructure | 6 | 40 |
| Development | 4 | 35 |
| Legal & Compliance | 5 | 25 |
| Architecture | 4 | 30 |
| **Total** | **26** | **185** |

## 🔄 Documentation Maintenance

### Update Frequency
- **API.md**: After API changes (pre-release)
- **DEPLOY.md**: When deployment configs change
- **README.md**: When major features added
- **Component READMEs**: When implementation changes

### Version Tracking
All docs reflect **v0.1.0-beta** (2024-01-16)

### Reporting Issues
Found outdated or incorrect documentation?
- Open GitHub issue with `[docs]` prefix
- Email docs@codeai.example.com

---

**Last Updated**: 2024-01-16  
**Version**: 0.1.0-beta  
**Status**: Complete and ready for beta launch
