"""Keep Python dataclasses and canonical JSON Schemas structurally aligned."""

import json
from dataclasses import asdict, fields
from pathlib import Path
from typing import Any, get_args

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from loop_schemas import models

ROOT = Path(__file__).resolve().parents[1]


def load_schema(name: str) -> dict[str, Any]:
    """Load one canonical schema."""
    return json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))


def properties_at(schema: dict[str, Any], *path: str) -> dict[str, Any]:
    """Navigate through nested `properties` and optional array `items` nodes."""
    node: dict[str, Any] = schema
    for part in path:
        if part == "[]":
            item = node.get("items")
            assert isinstance(item, dict)
            node = item
            continue
        properties = node.get("properties")
        assert isinstance(properties, dict)
        child = properties.get(part)
        assert isinstance(child, dict)
        node = child
    properties = node.get("properties")
    assert isinstance(properties, dict)
    return properties


def assert_field_parity(
    model_type: type[Any],
    schema: dict[str, Any],
    *path: str,
) -> None:
    """Require dataclass field names and schema properties to match exactly."""
    model_fields = {item.name for item in fields(model_type)}
    schema_fields = set(properties_at(schema, *path))
    assert model_fields == schema_fields


def omit_none(value: Any) -> Any:
    """Drop absent optional dataclass fields and normalize sequences for JSON."""
    if isinstance(value, dict):
        return {str(key): omit_none(item) for key, item in value.items() if item is not None}
    if isinstance(value, (list, tuple)):
        return [omit_none(item) for item in value]
    return value


def json_value(value: Any) -> Any:
    """Convert a dataclass to the JSON representation defined by the schemas."""
    return omit_none(asdict(value))


def validate_instance(schema_name: str, value: Any) -> None:
    """Validate a dataclass instance after canonical JSON conversion."""
    validator = Draft202012Validator(
        load_schema(schema_name),
        format_checker=FormatChecker(),
    )
    validator.validate(json_value(value))


def test_contract_model_matches_schema() -> None:
    """Check every contract dataclass and a representative round trip."""
    schema = load_schema("contract.schema.json")
    assert schema["properties"]["version"]["const"] == models.CONTRACT_DOCUMENT_VERSION
    mappings = [
        (models.Contract, ()),
        (models.Trigger, ("trigger",)),
        (models.Selection, ("selection",)),
        (models.Baseline, ("baseline",)),
        (models.Acceptance, ("acceptance",)),
        (models.Budgets, ("budgets",)),
        (models.Scope, ("scope",)),
        (models.Actions, ("actions",)),
        (models.HumanReview, ("human_review",)),
    ]
    for model_type, path in mappings:
        assert_field_parity(model_type, schema, *path)

    document = yaml.safe_load(
        (ROOT / "examples" / "harness-self-improvement.yaml").read_text(encoding="utf-8")
    )
    assert isinstance(document, dict)
    validate_instance("contract.schema.json", models.Contract.from_dict(document))


def test_evidence_model_matches_schema() -> None:
    """Check evidence dataclasses and a representative valid instance."""
    schema = load_schema("evidence.schema.json")
    assert schema["properties"]["version"]["const"] == models.EVIDENCE_DOCUMENT_VERSION
    mappings = [
        (models.Evidence, ()),
        (models.Environment, ("environment",)),
        (models.CommandResult, ("commands", "[]")),
        (models.Usage, ("usage",)),
        (models.TokenUsage, ("usage", "tokens")),
    ]
    for model_type, path in mappings:
        assert_field_parity(model_type, schema, *path)

    command_properties = properties_at(schema, "commands", "[]")
    assert set(get_args(models.ExecutionTermination)) == set(
        command_properties["termination"]["enum"]
    )

    value = models.Evidence(
        version=models.EVIDENCE_DOCUMENT_VERSION,
        run_id="run-001",
        contract_id="harness-self-improvement",
        repository="github.com/brunovicco/example",
        oid_algorithm="sha1",
        baseline_oid="a" * 40,
        candidate_oid="b" * 40,
        candidate_tree_sha256="1" * 64,
        contract_sha256="2" * 64,
        policy_sha256="3" * 64,
        environment=models.Environment(
            python="3.12.11",
            operating_system="linux",
            architecture="x86_64",
            executor_image="sha256:" + "9" * 64,
            working_directory="/workspace",
            sandbox_profile="linux-default-v1",
            uv_lock_sha256="c" * 64,
            tool_versions={"ruff": "0.15.21"},
        ),
        commands=(
            models.CommandResult(
                argv=("uv", "run", "pytest"),
                termination="EXITED",
                exit_code=0,
                stdout_sha256="d" * 64,
                stderr_sha256="e" * 64,
                specification_sha256="f" * 64,
                duration_s=1.25,
            ),
        ),
        changed_files=("src/example.py",),
        usage=models.Usage(
            provider="openai",
            model="example-model",
            tokens=models.TokenUsage(input=100, output=50),
            estimated_cost_usd=0.01,
        ),
        started_at="2026-07-18T12:00:00Z",
        finished_at="2026-07-18T12:00:02Z",
    )
    validate_instance("evidence.schema.json", value)


def test_verdict_model_matches_schema() -> None:
    """Check verdict dataclasses, enums, and a representative valid instance."""
    schema = load_schema("verdict.schema.json")
    assert schema["properties"]["version"]["const"] == models.VERDICT_DOCUMENT_VERSION
    mappings = [
        (models.Verdict, ()),
        (models.Justification, ("justification",)),
        (models.GateResult, ("justification", "gate_results", "[]")),
    ]
    for model_type, path in mappings:
        assert_field_parity(model_type, schema, *path)

    assert set(get_args(models.VerdictStatus)) == set(schema["properties"]["status"]["enum"])
    assert set(get_args(models.FinalState)) == set(schema["properties"]["final_state"]["enum"])
    assert set(get_args(models.ObjectIdAlgorithm)) == set(
        schema["properties"]["oid_algorithm"]["enum"]
    )

    value = models.Verdict(
        version=models.VERDICT_DOCUMENT_VERSION,
        run_id="run-001",
        contract_id="harness-self-improvement",
        oid_algorithm="sha1",
        candidate_oid="b" * 40,
        contract_sha256="c" * 64,
        evidence_sha256="e" * 64,
        status="PASS",
        justification=models.Justification(
            gate_results=(models.GateResult(gate="tests", passed=True),),
            summary="All hard gates passed.",
        ),
        final_state="SUCCEEDED",
        decided_at="2026-07-18T12:00:03Z",
    )
    validate_instance("verdict.schema.json", value)


def test_builder_result_model_matches_schema() -> None:
    """Check builder-result dataclasses and a representative valid instance."""
    schema = load_schema("builder-result.schema.json")
    assert schema["properties"]["version"]["const"] == models.BUILDER_RESULT_DOCUMENT_VERSION
    mappings = [
        (models.BuilderResult, ()),
        (models.SelfReported, ("self_reported",)),
        (models.Usage, ("usage",)),
        (models.TokenUsage, ("usage", "tokens")),
    ]
    for model_type, path in mappings:
        assert_field_parity(model_type, schema, *path)

    assert set(get_args(models.Confidence)) == set(
        schema["properties"]["self_reported"]["properties"]["confidence"]["enum"]
    )

    value = models.BuilderResult(
        version="1.0.0",
        run_id="run-001",
        contract_id="harness-self-improvement",
        baseline_sha="a" * 40,
        candidate_sha="b" * 40,
        summary="Prepared a candidate for independent verification.",
        changed_files=("src/example.py",),
        self_reported=models.SelfReported(
            gates_believed_passing=("tests",),
            confidence="medium",
        ),
        usage=models.Usage(
            provider="anthropic",
            model="example-model",
            tokens=models.TokenUsage(input=120, output=60),
        ),
        started_at="2026-07-18T12:00:00Z",
        finished_at="2026-07-18T12:00:02Z",
    )
    validate_instance("builder-result.schema.json", value)
