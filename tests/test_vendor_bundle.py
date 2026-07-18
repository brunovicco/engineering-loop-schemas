"""Regression tests for deterministic vendoring."""

import importlib.util
import json
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "render_vendor_bundle.py"
SPEC = importlib.util.spec_from_file_location("render_vendor_bundle", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_rendered_bundle_is_deterministic(tmp_path: Path) -> None:
    """The same source/version/commit must produce exactly the same bytes."""
    commit = "a" * 40
    expected = MODULE.expected_files(
        Path(__file__).resolve().parents[1],
        version="0.1.1",
        commit=commit,
        repository="brunovicco/engineering-loop-schemas",
    )
    MODULE.write_bundle(tmp_path, expected)
    assert MODULE.compare_bundle(tmp_path, expected) == []

    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["source"]["commit"] == commit
    assert manifest["source"]["version"] == "0.1.1"
    assert set(manifest["files"]) == {
        "__init__.py",
        "models.py",
        "validate_contract.py",
    }


def test_bundle_check_detects_tampering(tmp_path: Path) -> None:
    """A modified vendored file must fail the offline integrity check."""
    expected = MODULE.expected_files(
        Path(__file__).resolve().parents[1],
        version="0.1.1",
        commit="b" * 40,
        repository="brunovicco/engineering-loop-schemas",
    )
    MODULE.write_bundle(tmp_path, expected)
    (tmp_path / "models.py").write_text("# tampered\n", encoding="utf-8")

    errors = MODULE.compare_bundle(tmp_path, expected)
    assert any("drift detected in models.py" in error for error in errors)
