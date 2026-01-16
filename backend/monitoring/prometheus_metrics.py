"""Prometheus metrics exporter for monitoring."""
from prometheus_client import Counter, Histogram, Gauge, generate_latest


# Define metrics
inference_requests = Counter(
    'inference_requests_total',
    'Total inference requests',
    ['status', 'model']
)

inference_latency = Histogram(
    'inference_latency_seconds',
    'Inference latency in seconds',
    ['model'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0)
)

tokens_generated = Counter(
    'tokens_generated_total',
    'Total tokens generated',
    ['model']
)

api_errors = Counter(
    'api_errors_total',
    'Total API errors',
    ['error_type']
)

active_requests = Gauge(
    'active_requests',
    'Currently active requests'
)


def export_metrics():
    """Export metrics in Prometheus format."""
    return generate_latest()


if __name__ == '__main__':
    # Example usage
    inference_requests.labels(status='success', model='starcoder').inc()
    inference_latency.labels(model='starcoder').observe(0.234)
    tokens_generated.labels(model='starcoder').inc(150)
    
    print(export_metrics().decode('utf-8'))
