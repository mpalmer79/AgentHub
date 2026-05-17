"""Tests for the per-task token budget."""
import pytest

from app.core.budget import BudgetExceeded, TokenBudget


def test_records_tokens_and_iterations():
    b = TokenBudget(max_tokens=1000)
    b.record(100, 50)
    b.record(200, 100)
    assert b.input_tokens == 300
    assert b.output_tokens == 150
    assert b.total_tokens == 450
    assert b.iterations == 2


def test_raises_when_budget_exceeded():
    b = TokenBudget(max_tokens=100)
    b.record(50, 30)
    with pytest.raises(BudgetExceeded):
        b.record(50, 50)


def test_zero_budget_disables_check():
    b = TokenBudget(max_tokens=0)
    b.record(1_000_000, 1_000_000)
    assert b.total_tokens == 2_000_000  # no raise


def test_none_token_counts_are_treated_as_zero():
    b = TokenBudget(max_tokens=1000)
    b.record(None, None)
    assert b.total_tokens == 0
    assert b.iterations == 1
