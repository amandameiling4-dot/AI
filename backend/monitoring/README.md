# Monitoring & observability

Setup monitoring, logging, and metrics collection for the Code AI service.

## Components

- **Metrics collector** (`metrics.py`): Record inference latency, tokens, errors to JSONL
- **Logging** (`logging_config.py`): Rotating file logs + console output
- **Prometheus** (`prometheus_metrics.py`): Exportable metrics for Prometheus scraping
- **Middleware** (`middleware.py`): FastAPI integration for automatic request tracking

## Usage

### In the API server

```python
from fastapi import FastAPI
from backend.monitoring.middleware import add_monitoring_middleware

app = FastAPI()
app = add_monitoring_middleware(app)

# Now all requests are logged and metrics are exported at /metrics
```

### View metrics

```bash
curl http://localhost:8000/metrics
```

### Check JSONL metrics file

```bash
tail -f metrics/latest.jsonl
```

## Prometheus setup

Add to `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'code-ai'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

Then run:

```bash
prometheus --config.file=prometheus.yml
```

Visit `http://localhost:9090` for Prometheus UI.

## Key metrics

- `inference_requests_total` — count by status and model
- `inference_latency_seconds` — histogram of request latency
- `tokens_generated_total` — count of tokens generated
- `api_errors_total` — count of errors by type
- `active_requests` — gauge of in-flight requests
