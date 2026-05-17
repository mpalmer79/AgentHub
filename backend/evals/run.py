"""Entrypoint: `python -m evals.run` from the backend/ directory.

CI failure is the goal. If any case fails, exit non-zero.
"""

from __future__ import annotations

import sys

from evals.cases import CASES
from evals.harness import print_results, run_suite


def main() -> int:
    passed, total, results = run_suite(CASES)
    print_results(results)
    print(f"\n{passed}/{total} eval cases passed.")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
