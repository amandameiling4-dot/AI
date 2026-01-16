"""Tests for evaluation and benchmarking utilities."""
import pytest
from scripts.eval.evaluate import evaluate_completions, code_snippet_quality
from scripts.eval.performance import PerformanceBenchmark


def test_humaneval_benchmark():
    """Test HumanEval benchmark loading."""
    from scripts.eval.humaneval import HumanEvalBenchmark
    benchmark = HumanEvalBenchmark()
    # Should not raise; gracefully handles missing file
    assert isinstance(benchmark.problems, dict)


def test_performance_benchmark_latency():
    """Test latency measurement."""
    benchmark = PerformanceBenchmark()
    
    def sample_fn():
        import time
        time.sleep(0.01)
        return 'result'
    
    result = benchmark.measure_latency(sample_fn)
    assert 'latency_ms' in result
    assert result['latency_ms'] >= 10  # At least 10ms
    assert result['result'] == 'result'


def test_performance_benchmark_throughput():
    """Test throughput benchmark."""
    benchmark = PerformanceBenchmark()
    
    def fast_fn():
        return 42
    
    result = benchmark.benchmark_throughput(fast_fn, iterations=10)
    assert 'throughput_rps' in result
    assert result['iterations'] == 10
    assert result['throughput_rps'] > 0
    assert 'p95_latency_ms' in result
