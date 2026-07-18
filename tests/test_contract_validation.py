"""Behavioral tests for loop_schemas.validate_contract."""

import copy
from typing import Any

import pytest

from loop_schemas.validate_contract import SUPPORTED_HARD_GATES, validate


def _valid_contract() -> dict[str, Any]:
    return {
        "version": "1.0.0",
        "id": "harness-self-improvement",
        "objective": "Report-only self-evaluation of generated harness profiles.",
        "trigger": {"type": "manual"},
        "selection": {"strategy": "single-issue", "max_items": 1},
        "baseline": {"commands": ["uv run python scripts/quality_gate.py"]},
        "acceptance": {"hard_gates": ["lint", "typing", "tests"]},
        "budgets": {"max_tokens": 200000, "max_cost_usd": 5.0},
        "scope": {"allowlist": ["docs/**"], "denylist": [".loop/**", "scripts/loop_*"]},
        "actions": {"allowed": ["read", "propose_patch"], "denied": ["merge", "push"]},
        "human_review": {"required": True, "reviewers": ["@brunovicco"]},
    }


def test_valid_contract_has_no_errors() -> None:
    assert validate(_valid_contract()) == []


def test_missing_required_field_is_reported() -> None:
    contract = _valid_contract()
    del contract["objective"]
    errors = validate(contract)
    assert errors
    assert "objective" in errors[0]


def test_overlapping_allow_and_deny_globs_are_rejected() -> None:
    contract = _valid_contract()
    contract["scope"]["allowlist"] = ["docs/**", "scripts/loop_*"]
    contract["scope"]["denylist"] = [".loop/**", "scripts/loop_*"]
    errors = validate(contract)
    assert any("scripts/loop_*" in error for error in errors)


def test_empty_glob_is_rejected() -> None:
    contract = _valid_contract()
    contract["scope"]["allowlist"] = [""]
    errors = validate(contract)
    assert any("not a syntactically valid glob" in error for error in errors)


@pytest.mark.parametrize(
    "field",
    ["max_tokens", "max_cost_usd", "max_wall_clock_minutes", "max_commands"],
)
def test_non_positive_budget_is_rejected(field: str) -> None:
    contract = _valid_contract()
    contract["budgets"][field] = 0
    errors = validate(contract)
    assert any(field in error for error in errors)


def test_unsupported_hard_gate_is_rejected() -> None:
    contract = _valid_contract()
    contract["acceptance"]["hard_gates"] = ["lint", "vibes"]
    errors = validate(contract)
    assert any("vibes" in error for error in errors)


def test_every_declared_supported_gate_passes_alone() -> None:
    for gate in SUPPORTED_HARD_GATES:
        contract = _valid_contract()
        contract["acceptance"]["hard_gates"] = [gate]
        assert validate(contract) == []


def test_schedule_trigger_without_schedule_is_rejected() -> None:
    contract = _valid_contract()
    contract["trigger"] = {"type": "schedule"}
    errors = validate(contract)
    assert any("trigger.schedule" in error for error in errors)


def test_event_trigger_without_event_is_rejected() -> None:
    contract = _valid_contract()
    contract["trigger"] = {"type": "event"}
    errors = validate(contract)
    assert any("trigger.event" in error for error in errors)


def test_validate_does_not_mutate_input() -> None:
    contract = _valid_contract()
    snapshot = copy.deepcopy(contract)
    validate(contract)
    assert contract == snapshot
