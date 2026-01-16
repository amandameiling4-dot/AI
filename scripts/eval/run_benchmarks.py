"""Benchmark suite runner."""
import json
from pathlib import Path
from typing import Dict


class BenchmarkRunner:
    """Run and report on multiple benchmarks."""

    def __init__(self, output_dir: str = 'benchmark_results'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results = {}

    def run_all_benchmarks(self) -> Dict:
        """Run evaluation, performance, and HumanEval benchmarks."""
        from scripts.eval.evaluate import evaluate_completions
        from scripts.eval.performance import PerformanceBenchmark
        from scripts.eval.humaneval import HumanEvalBenchmark

        # Dummy data for demo
        preds = ['def foo():\n    return 1', 'x = 5']
        refs = ['def foo():\n    return 1', 'y = 10']

        print('Running evaluation benchmark...')
        eval_result = evaluate_completions(preds, refs)
        self.results['evaluation'] = eval_result

        print('Running performance benchmark...')
        perf_bench = PerformanceBenchmark()
        
        def dummy_inference():
            return 'def foo():\n    pass'
        
        perf_result = perf_bench.benchmark_throughput(dummy_inference, iterations=5)
        self.results['performance'] = perf_result

        print('HumanEval benchmark...')
        try:
            humaneval = HumanEvalBenchmark()
            self.results['humaneval_loaded'] = len(humaneval.problems) > 0
        except Exception as e:
            self.results['humaneval_error'] = str(e)

        return self.results

    def save_results(self, filename: str = 'results.json'):
        """Save results to JSON."""
        output_file = self.output_dir / filename
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f'Results saved to {output_file}')

    def print_summary(self):
        """Print results summary."""
        print('\n=== Benchmark Summary ===\n')
        for key, value in self.results.items():
            print(f'{key}:')
            if isinstance(value, dict):
                for k, v in value.items():
                    if isinstance(v, float):
                        print(f'  {k}: {v:.4f}')
                    else:
                        print(f'  {k}: {v}')
            else:
                print(f'  {value}')
            print()


if __name__ == '__main__':
    runner = BenchmarkRunner()
    runner.run_all_benchmarks()
    runner.print_summary()
    runner.save_results()
