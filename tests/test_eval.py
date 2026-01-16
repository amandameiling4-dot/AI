"""Test suite for evaluation utilities."""
from scripts.eval.evaluate import evaluate_completions, code_snippet_quality


def test_evaluate_completions_exact_match():
    preds = ['def foo():\n    return 1', 'x = 5', 'print("hello")']
    refs = ['def foo():\n    return 1', 'y = 10', 'print("hello")']
    result = evaluate_completions(preds, refs)
    assert result['exact_match_rate'] == 2 / 3
    assert result['total_samples'] == 3


def test_code_snippet_quality():
    code = 'def foo():\n    return 1'
    quality = code_snippet_quality(code)
    assert quality['is_non_empty']
    assert quality['has_indentation']
    assert quality['likely_valid']
