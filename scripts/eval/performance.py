"""Performance benchmarking utilities."""
import time
from typing import Callable, Dict
import statistics


class PerformanceBenchmark:
    """Benchmark latency and throughput of code completions."""

    def __init__(self):
        self.results = []

    def measure_latency(self, func: Callable, *args, **kwargs) -> Dict:
        """Measure latency of a single function call.
        
        Returns: {latency_ms, result}
        """
        start = time.time()
        result = func(*args, **kwargs)
        latency_ms = (time.time() - start) * 1000
        return {'latency_ms': latency_ms, 'result': result}

    def benchmark_throughput(self, func: Callable, iterations: int = 100, *args, **kwargs) -> Dict:
        """Measure throughput (requests per second).
        
        Returns: {avg_latency_ms, p50_ms, p95_ms, p99_ms, throughput_rps}
        """
        latencies = []
        start = time.time()
        
        for _ in range(iterations):
            m = self.measure_latency(func, *args, **kwargs)
            latencies.append(m['latency_ms'])
        
        total_time = time.time() - start
        throughput_rps = iterations / total_time
        
        sorted_latencies = sorted(latencies)
        return {
            'iterations': iterations,
            'avg_latency_ms': statistics.mean(latencies),
            'median_latency_ms': statistics.median(latencies),
            'p95_latency_ms': sorted_latencies[int(len(sorted_latencies) * 0.95)],
            'p99_latency_ms': sorted_latencies[int(len(sorted_latencies) * 0.99)],
            'max_latency_ms': max(latencies),
            'throughput_rps': throughput_rps,
        }

    def benchmark_memory(self, func: Callable, *args, **kwargs) -> Dict:
        """Measure peak memory usage (requires psutil)."""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            
            mem_before = process.memory_info().rss / 1024 / 1024  # MB
            result = func(*args, **kwargs)
            mem_after = process.memory_info().rss / 1024 / 1024  # MB
            
            return {
                'memory_before_mb': mem_before,
                'memory_after_mb': mem_after,
                'memory_delta_mb': mem_after - mem_before,
                'result': result,
            }
        except ImportError:
            return {'error': 'psutil not installed'}


if __name__ == '__main__':
    benchmark = PerformanceBenchmark()
    
    # Example benchmark
    def slow_function():
        time.sleep(0.1)
        return 'done'
    
    result = benchmark.benchmark_throughput(slow_function, iterations=5)
    print('Throughput benchmark:', result)
