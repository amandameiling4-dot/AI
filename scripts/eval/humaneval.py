"""HumanEval benchmark integration for code model evaluation."""
import json
from typing import List, Dict, Tuple
import subprocess
from pathlib import Path


class HumanEvalBenchmark:
    """Evaluate code completions on HumanEval tasks."""

    HUMANEVAL_PROBLEMS_URL = 'https://raw.githubusercontent.com/openai/human-eval/master/data/HumanEval.jsonl.gz'

    def __init__(self, data_dir: str = 'benchmarks/humaneval'):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.problems = self._load_problems()

    def _load_problems(self) -> Dict:
        """Load HumanEval problems."""
        problems_file = self.data_dir / 'HumanEval.jsonl'
        
        if not problems_file.exists():
            print(f'Note: Download HumanEval problems from {self.HUMANEVAL_PROBLEMS_URL}')
            return {}

        problems = {}
        with open(problems_file, 'r') as f:
            for line in f:
                prob = json.loads(line)
                problems[prob['task_id']] = prob
        return problems

    def evaluate_completion(self, task_id: str, completion: str, timeout: int = 10) -> Tuple[bool, str]:
        """Evaluate a single completion by running tests.
        
        Returns: (passed, error_message)
        """
        if task_id not in self.problems:
            return False, f'Task {task_id} not found'

        problem = self.problems[task_id]
        full_code = problem['prompt'] + completion
        test_code = f"""{full_code}
{problem['test']}
"""
        try:
            result = subprocess.run(
                ['python', '-c', test_code],
                capture_output=True,
                timeout=timeout,
                text=True,
            )
            if result.returncode == 0:
                return True, ''
            else:
                return False, result.stderr or result.stdout
        except subprocess.TimeoutExpired:
            return False, 'Timeout'
        except Exception as e:
            return False, str(e)

    def evaluate_batch(self, completions: Dict[str, str], timeout: int = 10) -> Dict:
        """Evaluate multiple completions.
        
        Args:
            completions: Dict of {task_id: completion_code}
        Returns:
            {task_id: {'passed': bool, 'error': str}}
        """
        results = {}
        for task_id, completion in completions.items():
            passed, error = self.evaluate_completion(task_id, completion, timeout)
            results[task_id] = {'passed': passed, 'error': error}
        return results

    def compute_pass_at_k(self, results: Dict, k: int = 1) -> float:
        """Compute pass@k metric.
        
        For k=1: simple pass rate
        For k>1: requires multiple samples per task (not implemented here)
        """
        if k != 1:
            raise NotImplementedError('pass@k for k>1 requires multiple samples per task')
        
        total = len(results)
        passed = sum(1 for r in results.values() if r['passed'])
        return passed / total if total > 0 else 0


if __name__ == '__main__':
    benchmark = HumanEvalBenchmark()
    print(f'Loaded {len(benchmark.problems)} HumanEval problems')
    
    # Example: evaluate a simple task (if loaded)
    if benchmark.problems:
        task_id = list(benchmark.problems.keys())[0]
        print(f'Example task: {task_id}')
        problem = benchmark.problems[task_id]
        print(f'Prompt: {problem["prompt"]}')
