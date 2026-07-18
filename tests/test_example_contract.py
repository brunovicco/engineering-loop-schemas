"""The shipped example contract must satisfy both the JSON Schema and validate_contract."""

import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from loop_schemas.validate_contract import load_document, validate


def test_example_contract_matches_json_schema(schemas_dir: Path, examples_dir: Path) -> None:
    schema = json.loads((schemas_dir / "contract.schema.json").read_text(encoding="utf-8"))
    document = yaml.safe_load(
        (examples_dir / "harness-self-improvement.yaml").read_text(encoding="utf-8")
    )
    Draft202012Validator(schema).validate(document)


def test_example_contract_passes_validate_contract(examples_dir: Path) -> None:
    document = load_document(examples_dir / "harness-self-improvement.yaml")
    assert validate(document) == []
