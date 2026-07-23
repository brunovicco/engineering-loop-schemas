"""Static security checks for GitHub Actions workflows."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FULL_COMMIT_USE = re.compile(r"^\s*uses:\s+[^@\s]+@[0-9a-f]{40}(?:\s+#.*)?$")


def test_every_external_action_is_pinned_to_a_full_commit() -> None:
    workflows = sorted((ROOT / ".github" / "workflows").glob("*.yml"))
    assert workflows
    for workflow in workflows:
        for line_number, line in enumerate(
            workflow.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            if line.lstrip().startswith("uses:"):
                assert FULL_COMMIT_USE.fullmatch(line), f"{workflow}:{line_number}: {line}"


def test_release_evidence_has_attestation_permissions_and_no_publish_step() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release-evidence.yml").read_text(encoding="utf-8")
    assert "id-token: write" in workflow
    assert "attestations: write" in workflow
    assert "artifact-metadata: write" in workflow
    assert "anchore/sbom-action@" in workflow
    assert workflow.count("actions/attest@") == 2
    assert "pypi" not in workflow.lower()
    assert "gh release create" not in workflow
