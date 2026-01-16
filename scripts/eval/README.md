# Evaluation scripts quick-start

Utilities for evaluating trained code models:

## Completions evaluation
```bash
python scripts/eval/evaluate.py
```

Metrics:
- Exact match rate
- Contain match rate (soft match)
- Code quality heuristics (non-empty, has indentation, likely valid syntax)

## HumanEval benchmark
```bash
# First download HumanEval problems
# Then:
python scripts/eval/humaneval.py
```

Metrics:
- Pass@1, Pass@k (requires multiple samples per task)
- Task-level pass/fail
- Execution timeout handling

## Performance benchmarking
```bash
python scripts/eval/performance.py
```

Metrics:
- Inference latency (p50, p95, p99)
- Throughput (requests/sec)
- Memory usage (peak, delta)

## Full benchmark suite
```bash
python scripts/eval/run_benchmarks.py
```

Generates `benchmark_results/results.json` with all metrics.
