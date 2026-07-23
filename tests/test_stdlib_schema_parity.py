"""Differential tests between the stdlib evaluator and jsonschema."""

import copy
from typing import Any

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from loop_schemas._stdlib_jsonschema import (
    UnsupportedSchemaError,
    assert_supported_schema,
)
from loop_schemas.schema_resources import DocumentKind, load_schema
from loop_schemas.validate_contract import validate_document


def contract_document() -> dict[str, Any]:
    return {
        "version": "1.0.0",
        "id": "example-contract",
        "objective": "Evaluate one candidate.",
        "trigger": {"type": "manual"},
        "selection": {"strategy": "single-issue", "max_items": 1},
        "baseline": {"commands": ["uv run pytest"]},
        "acceptance": {"hard_gates": ["tests"]},
        "budgets": {"max_tokens": 100},
        "scope": {"allowlist": ["src/**"], "denylist": [".git/**"]},
        "actions": {"allowed": ["read"], "denied": ["push"]},
        "human_review": {"required": True},
    }


def evidence_document() -> dict[str, Any]:
    return {
        "version": "2.0.0",
        "run_id": "run-001",
        "contract_id": "example-contract",
        "repository": "github.com/example/project",
        "oid_algorithm": "sha1",
        "baseline_oid": "a" * 40,
        "candidate_oid": "b" * 40,
        "candidate_tree_sha256": "c" * 64,
        "contract_sha256": "d" * 64,
        "policy_sha256": "e" * 64,
        "environment": {
            "python": "3.13.14",
            "operating_system": "linux",
            "architecture": "x86_64",
            "executor_image": "sha256:" + "f" * 64,
            "working_directory": "/workspace",
            "sandbox_profile": "linux-default-v1",
            "uv_lock_sha256": "0" * 64,
            "tool_versions": {"pytest": "9.1.1"},
        },
        "commands": [
            {
                "argv": ["uv", "run", "pytest"],
                "termination": "EXITED",
                "exit_code": 0,
                "stdout_sha256": "1" * 64,
                "stderr_sha256": "2" * 64,
                "specification_sha256": "3" * 64,
                "duration_s": 1.25,
            }
        ],
        "changed_files": ["src/example.py"],
        "usage": {
            "provider": "openai",
            "model": "example-model",
            "tokens": {"input": 10, "output": 5},
        },
        "started_at": "2026-07-23T10:00:00Z",
        "finished_at": "2026-07-23T10:00:02Z",
    }


def verdict_document() -> dict[str, Any]:
    return {
        "version": "2.0.0",
        "run_id": "run-001",
        "contract_id": "example-contract",
        "oid_algorithm": "sha1",
        "candidate_oid": "b" * 40,
        "contract_sha256": "d" * 64,
        "evidence_sha256": "e" * 64,
        "status": "PASS",
        "justification": {
            "gate_results": [{"gate": "tests", "passed": True}],
            "summary": "All gates passed.",
        },
        "final_state": "SUCCEEDED",
        "decided_at": "2026-07-23T10:00:03Z",
    }


def builder_result_document() -> dict[str, Any]:
    return {
        "version": "1.0.0",
        "run_id": "run-001",
        "contract_id": "example-contract",
        "baseline_sha": "a" * 40,
        "candidate_sha": "b" * 40,
        "summary": "Prepared a candidate.",
        "changed_files": ["src/example.py"],
        "self_reported": {
            "gates_believed_passing": ["tests"],
            "confidence": "medium",
        },
        "usage": {
            "provider": "openai",
            "model": "example-model",
            "tokens": {"input": 10, "output": 5},
        },
        "started_at": "2026-07-23T10:00:00Z",
        "finished_at": "2026-07-23T10:00:02Z",
    }


def assert_parity(kind: DocumentKind, document: dict[str, Any]) -> None:
    schema = load_schema(kind)
    reference = Draft202012Validator(schema, format_checker=FormatChecker())
    reference_valid = not list(reference.iter_errors(document))
    stdlib_valid = not validate_document(document, kind)
    assert stdlib_valid == reference_valid


@pytest.mark.parametrize(
    ("kind", "factory"),
    [
        ("contract", contract_document),
        ("evidence", evidence_document),
        ("verdict", verdict_document),
        ("builder-result", builder_result_document),
    ],
)
def test_valid_documents_have_validator_parity(
    kind: DocumentKind,
    factory,
) -> None:
    assert_parity(kind, factory())


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("unexpected",), True),
        (("version",), "latest"),
        (("trigger", "type"), "cron"),
        (("acceptance", "hard_gates"), []),
        (("baseline", "commands"), "uv run pytest"),
        (("budgets", "max_tokens"), "1"),
        (("acceptance", "hard_gates"), ["tests", "tests"]),
        (("trigger",), {"type": "manual", "schedule": "* * * * *"}),
    ],
)
def test_adversarial_contracts_have_validator_parity(
    path: tuple[str, ...],
    value: Any,
) -> None:
    document = contract_document()
    target = document
    for part in path[:-1]:
        target = target[part]
    target[path[-1]] = value
    assert_parity("contract", document)
    assert validate_document(document, "contract")


@pytest.mark.parametrize(
    ("kind", "factory", "path", "value"),
    [
        ("evidence", evidence_document, ("candidate_oid",), "b" * 12),
        ("evidence", evidence_document, ("commands", 0, "argv"), "uv run pytest"),
        ("evidence", evidence_document, ("environment", "architecture"), ""),
        ("verdict", verdict_document, ("version",), "1.0.0"),
        ("verdict", verdict_document, ("final_state",), "VERIFY_FAILED"),
        (
            "verdict",
            verdict_document,
            ("justification", "gate_results", 0, "passed"),
            False,
        ),
        ("builder-result", builder_result_document, ("candidate_sha",), "b" * 12),
        (
            "builder-result",
            builder_result_document,
            ("changed_files",),
            ["src/example.py", "src/example.py"],
        ),
    ],
)
def test_other_invalid_documents_have_validator_parity(
    kind: DocumentKind,
    factory,
    path: tuple[str | int, ...],
    value: Any,
) -> None:
    document = copy.deepcopy(factory())
    target: Any = document
    for part in path[:-1]:
        target = target[part]
    target[path[-1]] = value
    assert_parity(kind, document)
    assert validate_document(document, kind)


def test_stdlib_validator_enforces_date_time_format_without_optional_dependencies() -> None:
    document = evidence_document()
    document["started_at"] = "yesterday"
    errors = validate_document(document, "evidence")
    assert any("date-time" in error for error in errors)


def test_every_canonical_schema_uses_only_supported_keywords() -> None:
    for kind in ("contract", "evidence", "verdict", "builder-result"):
        assert_supported_schema(load_schema(kind))


def test_unknown_schema_keyword_fails_closed() -> None:
    with pytest.raises(UnsupportedSchemaError, match="unsupported"):
        assert_supported_schema({"type": "string", "mysteryAssertion": True})
