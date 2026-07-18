"""Shared fixtures: repo paths reused across the test suite."""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def schemas_dir() -> Path:
    """Return the schemas/ directory."""
    return ROOT / "schemas"


@pytest.fixture
def examples_dir() -> Path:
    """Return the examples/ directory."""
    return ROOT / "examples"
