"""Tests for monitoring and metrics."""
import json
from pathlib import Path
from backend.monitoring.metrics import MetricsCollector


def test_metrics_collector_record_inference():
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        collector = MetricsCollector(metrics_file=f'{tmpdir}/metrics.jsonl')
        collector.record_inference('test-key', tokens_generated=100, latency_ms=150.5)
        
        metrics_file = Path(tmpdir) / 'metrics.jsonl'
        assert metrics_file.exists()
        
        with open(metrics_file, 'r') as f:
            line = f.readline()
            record = json.loads(line)
            assert record['tokens'] == 100
            assert record['latency_ms'] == 150.5
            assert record['status'] == 'success'


def test_metrics_collector_summary():
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        collector = MetricsCollector(metrics_file=f'{tmpdir}/metrics.jsonl')
        collector.record_inference('test-key', tokens_generated=100, latency_ms=100)
        collector.record_inference('test-key', tokens_generated=200, latency_ms=200)
        collector.record_error('test-key', error_type='timeout')
        
        summary = collector.get_summary()
        assert summary['total_requests'] == 3
        assert summary['successes'] == 2
        assert summary['errors'] == 1
        assert summary['total_tokens'] == 300
        assert summary['error_rate'] > 0
