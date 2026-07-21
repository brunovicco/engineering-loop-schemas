"""Keep every public package-version declaration aligned."""

import tomllib
from importlib.metadata import version as distribution_version
from pathlib import Path

import loop_schemas

ROOT = Path(__file__).resolve().parents[1]


def test_runtime_version_matches_project_metadata() -> None:
    """The importable and build metadata versions must never drift."""
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert (
        loop_schemas.__version__
        == project["project"]["version"]
        == distribution_version("loop-schemas")
    )
