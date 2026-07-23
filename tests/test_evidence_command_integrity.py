"""Adversarial checks for command-result evidence integrity."""

import copy
import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

ROOT = Path(__file__).resolve().parents[1]


def evidence_document() -> dict[str, Any]:
    """Return a minimal valid evidence document."""
    return {
        "version": "2.0.0",
        "run_id": "run-001",
        "contract_id": "harness-self-improvement",
        "repository": "github.com/brunovicco/example",
        "oid_algorithm": "sha1",
        "baseline_oid": "a" * 40,
        "candidate_oid": "b" * 40,
        "candidate_tree_sha256": "1" * 64,
        "contract_sha256": "2" * 64,
        "policy_sha256": "3" * 64,
        "environment": {
            "python": "3.12.11",
            "operating_system": "linux",
            "architecture": "x86_64",
            "executor_image": "sha256:" + "9" * 64,
            "working_directory": "/workspace",
            "sandbox_profile": "linux-default-v1",
            "uv_lock_sha256": "c" * 64,
            "tool_versions": {"pytest": "9.0.2"},
        },
        "commands": [
            {
                "argv": ["uv", "run", "pytest"],
                "termination": "EXITED",
                "exit_code": 0,
                "stdout_sha256": "d" * 64,
                "stderr_sha256": "e" * 64,
                "specification_sha256": "f" * 64,
                "duration_s": 1.25,
            }
        ],
        "changed_files": ["src/example.py"],
        "usage": {
            "provider": "openai",
            "model": "example-model",
            "tokens": {"input": 100, "output": 50},
        },
        "started_at": "2026-07-21T12:00:00Z",
        "finished_at": "2026-07-21T12:00:02Z",
    }


@pytest.fixture
def validator() -> Draft202012Validator:
    """Load the canonical evidence schema."""
    schema = json.loads((ROOT / "schemas" / "evidence.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def test_exited_command_requires_integer_exit_code(
    validator: Draft202012Validator,
) -> None:
    """Natural process exit retains its real integer exit code."""
    document = evidence_document()
    validator.validate(document)

    document["commands"][0]["exit_code"] = None
    with pytest.raises(ValidationError):
        validator.validate(document)


@pytest.mark.parametrize("termination", ["TIMED_OUT", "CANCELLED", "OUTPUT_LIMIT"])
def test_forced_termination_requires_null_exit_code(
    validator: Draft202012Validator,
    termination: str,
) -> None:
    """Forced termination is typed and never invents a process exit code."""
    document = evidence_document()
    document["commands"][0]["termination"] = termination
    document["commands"][0]["exit_code"] = None
    validator.validate(document)

    document["commands"][0]["exit_code"] = 137
    with pytest.raises(ValidationError):
        validator.validate(document)


@pytest.mark.parametrize("field", ["stdout_sha256", "stderr_sha256", "specification_sha256"])
def test_every_integrity_hash_is_required(
    validator: Draft202012Validator,
    field: str,
) -> None:
    """No output stream or gate specification may remain unbound."""
    document = evidence_document()
    del document["commands"][0][field]

    with pytest.raises(ValidationError):
        validator.validate(document)


@pytest.mark.parametrize("field", ["stdout_sha256", "stderr_sha256", "specification_sha256"])
def test_every_integrity_hash_must_be_canonical_sha256(
    validator: Draft202012Validator,
    field: str,
) -> None:
    """Hashes are exactly 64 lowercase hexadecimal characters."""
    document = copy.deepcopy(evidence_document())
    document["commands"][0][field] = "A" * 64

    with pytest.raises(ValidationError):
        validator.validate(document)


@pytest.mark.parametrize("field", ["baseline_oid", "candidate_oid"])
def test_git_object_ids_must_be_complete(
    validator: Draft202012Validator,
    field: str,
) -> None:
    """Abbreviated Git object IDs are ambiguous and therefore rejected."""
    document = evidence_document()
    document[field] = "a" * 12

    with pytest.raises(ValidationError):
        validator.validate(document)


def test_command_is_a_shell_free_argument_vector(
    validator: Draft202012Validator,
) -> None:
    """A display string cannot substitute for the executed argv."""
    document = evidence_document()
    document["commands"][0]["argv"] = "uv run pytest"

    with pytest.raises(ValidationError):
        validator.validate(document)
