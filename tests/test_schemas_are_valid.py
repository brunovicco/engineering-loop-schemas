"""Every schemas/*.schema.json must itself be a valid Draft 2020-12 schema."""

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

SCHEMA_NAMES = (
    "contract.schema.json",
    "evidence.schema.json",
    "verdict.schema.json",
    "builder-result.schema.json",
)


def test_repository_has_the_four_required_schemas(schemas_dir: Path) -> None:
    names = {path.name for path in schemas_dir.glob("*.schema.json")}
    assert names == set(SCHEMA_NAMES)


@pytest.mark.parametrize("name", SCHEMA_NAMES)
def test_schema_is_valid_json_schema(schemas_dir: Path, name: str) -> None:
    schema = json.loads((schemas_dir / name).read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
