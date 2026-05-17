"""Per-task token budget tracking.

Agents accumulate tokens across multiple model calls during a single
task. Without a ceiling, a poorly-prompted agent can run away with
spend. `TokenBudget` is checked after every model call and raises
`BudgetExceeded` when the cap is hit.
"""
from __future__ import annotations

from dataclasses import dataclass, field


class BudgetExceeded(RuntimeError):
    """Raised when a task exceeds its configured token budget."""


@dataclass
class TokenBudget:
    max_tokens: int
    input_tokens: int = 0
    output_tokens: int = 0
    iterations: int = field(default=0, init=False)

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    def record(self, input_tokens: int | None, output_tokens: int | None) -> None:
        self.iterations += 1
        self.input_tokens += int(input_tokens or 0)
        self.output_tokens += int(output_tokens or 0)
        if self.max_tokens > 0 and self.total_tokens > self.max_tokens:
            raise BudgetExceeded(
                f"Task exceeded token budget: {self.total_tokens} > {self.max_tokens}"
            )
