# Validation record

## Current candidate — unreleased

Validated on 2026-07-23 for the breaking-change candidate expected to become
`v0.3.0`.

### Identity and provenance

- Base release: `v0.2.0`.
- Base source commit:
  `4c17dfc7b58b0376a297b728b5ef8cae8c2d2bde`.
- The candidate is delivered as an uncommitted patch/ZIP; it does not claim a
  release commit or tag.
- Package version remains `0.2.0` until the dedicated release step.
- Document wire versions are independent: contract and builder-result
  `1.0.0`, evidence and verdict `2.0.0`.

The renderer now refuses to emit authenticated provenance from a dirty tree. A
consumer bundle must be generated only after these changes are committed, from
the final clean release commit.

### Results

- Python used for local validation: 3.13.14.
- Lockfile validation and frozen dependency installation: passed.
- Ruff lint and format check: passed.
- Pyright strict: zero errors and zero warnings.
- Test suite: 93 passed.
- Coverage: 92.04%, above the enforced 90% minimum.
- Wheel and source distribution: built successfully.
- Wheel contents: all four canonical schemas present under
  `loop_schemas/schemas/`.
- Contract, evidence, and verdict examples: validated.
- Dataclass and JSON Schema parity: passed.
- Adversarial stdlib/jsonschema differential suite: passed.
- Verdict status/final-state and contract gate completeness: passed.
- Deterministic bundle rendering and drift detection: passed.
- Source version, commit, origin, and clean-tree provenance checks: passed.
- Symlink, unexpected-file, and content-tampering rejection: passed.
- Python 3.12-3.14 lint-compatibility regression suite: passed.
- Release-evidence workflow added with full-commit-pinned SBOM, attestation, and artifact actions.

The GitHub Actions matrix remains authoritative for the final Python 3.12,
3.13, and 3.14 result after the branch is pushed. The SBOM and signed
attestations can only be produced and verified by the tag-triggered GitHub
workflow; they are not claimed by this local candidate.

### Artifact contents

The wheel now includes:

- public models and document-version constants;
- the fail-closed stdlib structural evaluator;
- the schema resource API;
- the document validator;
- contract, evidence, verdict, and builder-result schemas.

The deterministic vendor bundle now includes:

- `__init__.py`;
- `_stdlib_jsonschema.py`;
- `models.py`;
- `schema_resources.py`;
- `validate_contract.py`;
- `schemas/*.schema.json`;
- `manifest.json`.

Manifest version `2.0.0` binds every file to the source repository, package
version, full commit, file size, SHA-256, and declared import adaptations.

### Scope and limitations

This candidate remains report-only. It defines and validates contracts,
evidence, verdicts, and non-authoritative builder results. It does not:

- execute an engineering loop;
- modify product code;
- create or promote candidates;
- provide a state machine or evaluator runtime;
- merge branches;
- deploy artifacts;
- allow a builder to certify its own work.

JSON validation is standard-library-only. YAML input requires PyYAML.
RFC 8785/JCS hashing is a producer responsibility; this package defines the
required digest binding but does not execute trusted evidence collection.

### Reproduce

```bash
uv lock --check
uv sync --frozen --all-groups
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest
uv build
```

After committing the candidate on a clean branch:

```bash
uv run python scripts/render_vendor_bundle.py \
  --target build/vendor/_vendor_loop_schemas \
  --source-commit "$(git rev-parse HEAD)"

uv run python scripts/render_vendor_bundle.py \
  --target build/vendor/_vendor_loop_schemas \
  --source-commit "$(git rev-parse HEAD)" \
  --check
```

## Published baseline — `v0.2.0`

The published baseline release is
[`v0.2.0`](https://github.com/brunovicco/engineering-loop-schemas/releases/tag/v0.2.0),
from commit `4c17dfc7b58b0376a297b728b5ef8cae8c2d2bde`. It predates the structural
validator parity, installed schema resources, evidence/verdict `2.0.0`, and
authenticated source-provenance changes recorded above.
