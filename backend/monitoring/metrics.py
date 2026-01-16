"""Metrics collection and monitoring utilities."""
import time
from datetime import datetime
from typing import Dict, Optional
import json
from pathlib import Path


class MetricsCollector:
    """Collect and export metrics for monitoring."""

    def __init__(self, metrics_file: str = 'metrics/latest.jsonl'):
        self.metrics_file = Path(metrics_file)
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)

    def record_inference(
        self,
        api_key: str,
        tokens_generated: int,
        latency_ms: float,
        model: str = 'starcoder',
        status: str = 'success',
    ):
        """Record an inference request."""
        record = {
            'timestamp': datetime.utcnow().isoformat(),
            'api_key': api_key[:16] + '***' if len(api_key) > 16 else api_key,  # Redact
            'tokens': tokens_generated,
            'latency_ms': latency_ms,
            'model': model,
            'status': status,
        }
        with open(self.metrics_file, 'a') as f:
            f.write(json.dumps(record) + '\n')

    def record_error(self, api_key: str, error_type: str, model: str = 'starcoder'):
        """Record an error."""
        record = {
            'timestamp': datetime.utcnow().isoformat(),
            'api_key': api_key[:16] + '***',
            'error_type': error_type,
            'model': model,
            'status': 'error',
        }
        with open(self.metrics_file, 'a') as f:
            f.write(json.dumps(record) + '\n')

    def get_summary(self, hours: int = 24) -> Dict:
        """Get metrics summary for the past N hours."""
        if not self.metrics_file.exists():
            return {'total_requests': 0, 'errors': 0, 'avg_latency_ms': 0, 'total_tokens': 0}

        cutoff_time = datetime.utcnow().timestamp() - (hours * 3600)
        success_count = 0
        error_count = 0
        total_tokens = 0
        latencies = []

        with open(self.metrics_file, 'r') as f:
            for line in f:
                try:
                    record = json.loads(line)
                    ts = datetime.fromisoformat(record.get('timestamp', '2000-01-01')).timestamp()
                    if ts < cutoff_time:
                        continue
                    if record.get('status') == 'success':
                        success_count += 1
                        latencies.append(record.get('latency_ms', 0))
                        total_tokens += record.get('tokens', 0)
                    elif record.get('status') == 'error':
                        error_count += 1
                except Exception:
                    pass

        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        return {
            'period_hours': hours,
            'total_requests': success_count + error_count,
            'successes': success_count,
            'errors': error_count,
            'error_rate': error_count / (success_count + error_count) if (success_count + error_count) > 0 else 0,
            'avg_latency_ms': avg_latency,
            'p95_latency_ms': sorted(latencies)[int(len(latencies) * 0.95)] if len(latencies) > 1 else 0,
            'total_tokens': total_tokens,
        }


if __name__ == '__main__':
    collector = MetricsCollector()
    collector.record_inference('test-key', tokens_generated=150, latency_ms=234.5)
    collector.record_inference('test-key', tokens_generated=100, latency_ms=150.2)
    collector.record_error('test-key', error_type='timeout')
    
    summary = collector.get_summary(hours=24)
    print('Metrics summary:', summary)
