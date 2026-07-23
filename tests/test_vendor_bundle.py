"""Regression tests for deterministic vendoring."""

import importlib
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "render_vendor_bundle.py"
SPEC = importlib.util.spec_from_file_location("render_vendor_bundle", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def run_fixture_git(root: Path, *arguments: str) -> None:
    """Run one fixed Git command while constructing a local test repository."""
    git = shutil.which("git")
    assert git is not None
    subprocess.run(  # noqa: S603 -- executable and argv are test-controlled.
        [git, *arguments],
        cwd=root,
        check=True,
        capture_output=True,
    )


def test_rendered_bundle_is_deterministic(tmp_path: Path) -> None:
    """The same source/version/commit must produce exactly the same bytes."""
    commit = "a" * 40
    expected = MODULE.expected_files(
        Path(__file__).resolve().parents[1],
        version="0.2.0",
        commit=commit,
        repository="brunovicco/engineering-loop-schemas",
    )
    MODULE.write_bundle(tmp_path, expected)
    assert MODULE.compare_bundle(tmp_path, expected) == []

    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["source"]["commit"] == commit
    assert manifest["manifest_version"] == "2.0.0"
    assert manifest["source"]["version"] == "0.2.0"
    assert set(manifest["files"]) == {
        "__init__.py",
        "_stdlib_jsonschema.py",
        "models.py",
        "schema_resources.py",
        "validate_contract.py",
        "schemas/builder-result.schema.json",
        "schemas/contract.schema.json",
        "schemas/evidence.schema.json",
        "schemas/verdict.schema.json",
    }


def test_bundle_check_detects_tampering(tmp_path: Path) -> None:
    """A modified vendored file must fail the offline integrity check."""
    expected = MODULE.expected_files(
        Path(__file__).resolve().parents[1],
        version="0.2.0",
        commit="b" * 40,
        repository="brunovicco/engineering-loop-schemas",
    )
    MODULE.write_bundle(tmp_path, expected)
    (tmp_path / "models.py").write_text("# tampered\n", encoding="utf-8")

    errors = MODULE.compare_bundle(tmp_path, expected)
    assert any("drift detected in models.py" in error for error in errors)


def test_bundle_check_rejects_symlinks_and_unexpected_files(tmp_path: Path) -> None:
    """Integrity checks cover paths and file types, not just expected bytes."""
    expected = MODULE.expected_files(
        Path(__file__).resolve().parents[1],
        version="0.2.0",
        commit="c" * 40,
        repository="brunovicco/engineering-loop-schemas",
    )
    MODULE.write_bundle(tmp_path, expected)
    (tmp_path / "unexpected.txt").write_text("unexpected", encoding="utf-8")
    (tmp_path / "models.py").unlink()
    (tmp_path / "models.py").symlink_to(tmp_path / "__init__.py")

    errors = MODULE.compare_bundle(tmp_path, expected)
    assert any("unexpected vendored file" in error for error in errors)
    assert any("symbolic link" in error for error in errors)


def test_write_bundle_replaces_the_complete_previous_tree(tmp_path: Path) -> None:
    """A render removes stale nested content and leaves a complete new tree."""
    target = tmp_path / "bundle"
    (target / "old").mkdir(parents=True)
    (target / "old" / "stale.txt").write_text("stale", encoding="utf-8")
    expected = {"nested/file.txt": b"new\n"}

    MODULE.write_bundle(target, expected)

    assert (target / "nested" / "file.txt").read_bytes() == b"new\n"
    assert not (target / "old").exists()


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        (
            "https://github.com/brunovicco/engineering-loop-schemas.git",
            "brunovicco/engineering-loop-schemas",
        ),
        (
            "git@github.com:brunovicco/engineering-loop-schemas.git",
            "brunovicco/engineering-loop-schemas",
        ),
    ],
)
def test_repository_origin_is_normalized(url: str, expected: str) -> None:
    assert MODULE.normalize_repository(url) == expected


def test_source_identity_rejects_a_dirty_checkout(tmp_path: Path) -> None:
    """Declared provenance cannot be rendered over uncommitted bytes."""
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "fixture"\nversion = "1.2.3"\n',
        encoding="utf-8",
    )
    run_fixture_git(tmp_path, "init")
    run_fixture_git(tmp_path, "config", "user.email", "fixture@example.com")
    run_fixture_git(tmp_path, "config", "user.name", "Fixture")
    run_fixture_git(tmp_path, "config", "commit.gpgsign", "false")
    run_fixture_git(
        tmp_path,
        "remote",
        "add",
        "origin",
        "https://github.com/example/fixture.git",
    )
    run_fixture_git(tmp_path, "add", "pyproject.toml")
    run_fixture_git(tmp_path, "commit", "-m", "fixture")
    commit = MODULE.git_commit(tmp_path)
    MODULE.verify_source_identity(
        tmp_path,
        version="1.2.3",
        commit=commit,
        repository="example/fixture",
    )
    (tmp_path / "dirty.txt").write_text("dirty", encoding="utf-8")

    with pytest.raises(ValueError, match="not clean"):
        MODULE.verify_source_identity(
            tmp_path,
            version="1.2.3",
            commit=commit,
            repository="example/fixture",
        )


def test_renderer_cli_renders_checks_and_detects_drift(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys,
) -> None:
    """Exercise the user-facing render/check flow without weakening provenance."""
    root = Path(__file__).resolve().parents[1]
    target = tmp_path / "bundle"
    commit = "d" * 40

    def accept_test_identity(
        source_root: Path,
        *,
        version: str,
        commit: str,
        repository: str,
    ) -> None:
        del source_root, version, commit, repository

    monkeypatch.setattr(MODULE, "verify_source_identity", accept_test_identity)
    arguments = [
        "--target",
        str(target),
        "--source-root",
        str(root),
        "--source-version",
        "0.2.0",
        "--source-commit",
        commit,
    ]

    assert MODULE.main(arguments) == 0
    assert "Rendered" in capsys.readouterr().out
    assert MODULE.main([*arguments, "--check"]) == 0
    assert "matches" in capsys.readouterr().out

    (target / "models.py").write_text("# drift\n", encoding="utf-8")
    assert MODULE.main([*arguments, "--check"]) == 1
    assert "out of date" in capsys.readouterr().err


def test_renderer_cli_rejects_invalid_declared_provenance(
    tmp_path: Path,
    capsys,
) -> None:
    root = Path(__file__).resolve().parents[1]
    result = MODULE.main(
        [
            "--target",
            str(tmp_path / "bundle"),
            "--source-root",
            str(root),
            "--source-version",
            "latest",
            "--source-commit",
            "a" * 40,
        ]
    )
    assert result == 2
    assert "invalid source provenance" in capsys.readouterr().err


def test_renderer_rejects_non_directory_target(tmp_path: Path) -> None:
    target = tmp_path / "bundle"
    target.write_text("not a directory", encoding="utf-8")
    with pytest.raises(ValueError, match="not a directory"):
        MODULE.write_bundle(target, {"models.py": b"content"})


def test_project_version_and_repository_validation_fail_closed(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[build-system]\n", encoding="utf-8")
    with pytest.raises(ValueError, match="no \\[project\\]"):
        MODULE.project_version(tmp_path)
    with pytest.raises(ValueError, match="unsupported"):
        MODULE.normalize_repository("https://gitlab.com/example/project")


def test_vendored_sources_remain_provider_neutral() -> None:
    """Shared vendored sources must not depend on either harness identity."""
    source_root = Path(__file__).resolve().parents[1] / "src" / "loop_schemas"
    content = "\n".join(
        (source_root / name).read_text(encoding="utf-8")
        for name in ("models.py", "validate_contract.py")
    )

    forbidden_markers = (
        "Claude Code",
        "OpenAI Codex",
        ".claude",
        ".codex",
        "CLAUDE_",
        "CODEX_",
    )
    assert not [marker for marker in forbidden_markers if marker in content]


def test_rendered_bundle_is_self_contained_and_can_validate(tmp_path: Path) -> None:
    """The rendered package can load its schemas without the source package."""
    target = tmp_path / "_vendor_loop_schemas"
    expected = MODULE.expected_files(
        Path(__file__).resolve().parents[1],
        version="0.2.0",
        commit="e" * 40,
        repository="brunovicco/engineering-loop-schemas",
    )
    MODULE.write_bundle(target, expected)

    package_name = "_vendor_loop_schemas"
    spec = importlib.util.spec_from_file_location(
        package_name,
        target / "__init__.py",
        submodule_search_locations=[str(target)],
    )
    assert spec is not None and spec.loader is not None
    package = importlib.util.module_from_spec(spec)
    sys.modules[package_name] = package
    try:
        spec.loader.exec_module(package)
        validator = importlib.import_module(f"{package_name}.validate_contract")
        document = {
            "version": "1.0.0",
            "id": "example",
            "objective": "Validate the vendored package.",
            "trigger": {"type": "manual"},
            "selection": {"strategy": "single"},
            "baseline": {"commands": ["true"]},
            "acceptance": {"hard_gates": ["tests"]},
            "budgets": {"max_tokens": 1},
            "scope": {"allowlist": [], "denylist": []},
            "actions": {"allowed": [], "denied": []},
            "human_review": {"required": True},
        }
        assert validator.validate(document) == []
    finally:
        for name in list(sys.modules):
            if name == package_name or name.startswith(f"{package_name}."):
                del sys.modules[name]
