"""Evaluation suite for code model completions and generation quality.

Metrics:
- HumanEval pass@k (requires human eval fixture)
- Linter pass rate
- Latency benchmarks
"""
import json
from pathlib import Path
from typing import List, Dict, Tuple


def exact_match(generated: str, reference: str) -> bool:
    """Check for exact match (after stripping whitespace)."""
    return generated.strip() == reference.strip()


def contains_match(generated: str, reference: str) -> bool:
    """Check if reference is contained in generated (soft match)."""
    return reference.strip() in generated.strip()


def code_snippet_quality(code: str) -> Dict[str, bool]:
    """Quick heuristic checks for code quality."""
    has_syntax_error = False
    has_indentation = '\n' in code and any(l.startswith(' ') or l.startswith('\t') for l in code.split('\n'))
    is_non_empty = len(code.strip()) > 0

    return {
        'is_non_empty': is_non_empty,
        'has_indentation': has_indentation,
        'likely_valid': is_non_empty and has_indentation,
    }


def evaluate_completions(predictions: List[str], references: List[str]) -> Dict[str, float]:
    """Evaluate a batch of completions."""
    exact_matches = sum(1 for p, r in zip(predictions, references) if exact_match(p, r))
    contain_matches = sum(1 for p, r in zip(predictions, references) if contains_match(p, r))

    quality_scores = [code_snippet_quality(p) for p in predictions]
    avg_quality = sum(1 for q in quality_scores if q.get('likely_valid')) / len(quality_scores) if quality_scores else 0

    return {
        'exact_match_rate': exact_matches / len(predictions) if predictions else 0,
        'contain_match_rate': contain_matches / len(predictions) if predictions else 0,
        'code_quality_rate': avg_quality,
        'total_samples': len(predictions),
    }


if __name__ == '__main__':
    # Quick test
    preds = ['def foo():\n    return 1', 'x = 5', 'print("hello")']
    refs = ['def foo():\n    return 1', 'y = 10', 'print("hello")']
    result = evaluate_completions(preds, refs)
    print('Evaluation result:', result)
