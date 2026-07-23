"""Installed artifacts must carry the canonical schemas and public API."""

import shutil
import subprocess
from pathlib import Path
from zipfile import ZipFile

from loop_schemas import SCHEMA_FILENAMES, load_schema, schema_text

ROOT = Path(__file__).resolve().parents[1]


def test_every_schema_is_available_through_the_public_resource_api() -> None:
    for kind, filename in SCHEMA_FILENAMES.items():
        assert load_schema(kind)["$id"].endswith(filename)
        assert schema_text(kind).endswith("}\n")


def test_wheel_contains_every_canonical_schema(tmp_path: Path) -> None:
    uv = shutil.which("uv")
    assert uv is not None
    result = subprocess.run(  # noqa: S603 -- fixed local build command.
        [uv, "build", "--wheel", "--out-dir", str(tmp_path)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    wheel = next(tmp_path.glob("loop_schemas-*.whl"))
    with ZipFile(wheel) as archive:
        names = set(archive.namelist())

    expected = {f"loop_schemas/schemas/{filename}" for filename in SCHEMA_FILENAMES.values()}
    assert expected <= names
