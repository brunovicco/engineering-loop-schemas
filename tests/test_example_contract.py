"""The shipped example contract must satisfy both the JSON Schema and validate_contract."""

import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from loop_schemas.validate_contract import (
    load_document,
    validate,
    validate_evidence,
    validate_verdict,
)


def test_example_contract_matches_json_schema(schemas_dir: Path, examples_dir: Path) -> None:
    schema = json.loads((schemas_dir / "contract.schema.json").read_text(encoding="utf-8"))
    document = yaml.safe_load(
        (examples_dir / "harness-self-improvement.yaml").read_text(encoding="utf-8")
    )
    Draft202012Validator(schema).validate(document)


def test_example_contract_passes_validate_contract(examples_dir: Path) -> None:
    document = load_document(examples_dir / "harness-self-improvement.yaml")
    assert validate(document) == []


def test_example_evidence_and_verdict_are_valid(examples_dir: Path) -> None:
    contract = load_document(examples_dir / "harness-self-improvement.yaml")
    evidence = load_document(examples_dir / "trusted-evidence.json")
    verdict = load_document(examples_dir / "trusted-verdict.json")

    assert validate_evidence(evidence) == []
    assert validate_verdict(verdict, contract=contract) == []
