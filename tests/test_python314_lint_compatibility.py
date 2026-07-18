"""Regression guard: models.py must stay ruff-clean when vendored into a
Python-3.14-targeted project.

This project supports Python 3.12-3.14 and deliberately avoids
`from __future__ import annotations` (see models.py's module-level
comment) so it is safe to vendor into codebases that ban that import.
Self-referencing `from_dict` classmethod return annotations therefore stay
quoted for correctness on 3.12/3.13. Ruff's UP037 rule assumes PEP 649
lazy-annotation semantics whenever a caller's target-version is 3.14 and
flags those quotes as unnecessary in that single-version view -- which is
exactly what happened when this file was vendored into a harness project
rendered for Python 3.14 (see CHANGELOG.md). This test locks in the fix
against every target-version this project claims to support.
"""

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / "src/loop_schemas/models.py"
SUPPORTED_TARGET_VERSIONS = ("py312", "py313", "py314")


@pytest.mark.parametrize("target_version", SUPPORTED_TARGET_VERSIONS)
def test_models_lint_clean_for_every_supported_python(target_version: str) -> None:
    result = subprocess.run(  # noqa: S603 -- fixed argv, no shell.
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            f"--target-version={target_version}",
            str(MODELS),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
