"""Run the eval suite as part of pytest so any regression fails CI."""
from evals.cases import CASES
from evals.harness import run_suite


def test_all_eval_cases_pass():
    passed, total, results = run_suite(CASES)
    failures = [r for r in results if not r.passed]
    assert passed == total, "Failed eval cases:\n" + "\n".join(
        f"  - {r.name}: {r.detail}" for r in failures
    )


def test_eval_suite_is_non_empty():
    assert len(CASES) >= 3, "Eval suite shrunk — did you delete cases?"
