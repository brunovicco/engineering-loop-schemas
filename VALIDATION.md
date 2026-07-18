# Validation record

## Current validation — Phase 0-1

Validated on 2026-07-18 for release `v0.1.2`.

### Identity and provenance

- Published source commit:
  `0459d61b7b1d4e7b46709e6d3895770553e6fab0`.
- Release: `v0.1.2`.
- Final integration: pull request
  [#2](https://github.com/brunovicco/engineering-loop-schemas/pull/2).
- The pull-request quality run validated source head
  `f736dbf353e491a4cda9857eb995df881918d41d` before GitHub recreated the commit through squash
  merge:
  <https://github.com/brunovicco/engineering-loop-schemas/actions/runs/29660042662>.
- Consumers must record the published 40-character commit, not a branch name or the pre-squash
  pull-request head.

### Results

- Python 3.12, 3.13, and 3.14 CI matrix: passed.
- Lockfile validation and frozen dependency installation: passed.
- Ruff lint and format check: passed.
- Pyright strict: zero errors.
- Test suite: 33 passed.
- Coverage: 96.14%, above the enforced 80% minimum.
- Wheel and source distribution: built successfully.
- Contract examples: validated.
- Dataclass and JSON Schema parity: passed.
- Deterministic bundle rendering: passed.
- Bundle drift and tampering detection: passed.
- Provider-neutral source regression test: passed.

### Published consumer bundle

The deterministic renderer produces:

- `__init__.py`;
- `models.py`;
- `validate_contract.py`;
- `manifest.json`.

The manifest binds the bundle to the source repository, version, full commit, file sizes, SHA-256
hashes, and the declared package-import adaptation. The Codex and Claude harnesses consume the same
`v0.1.2` manifest and file hashes.

### Scope and limitations

This release is Phase 0-1 and strictly report-only. It defines and validates contracts, evidence,
verdicts, and non-authoritative builder results. It does not:

- execute an engineering loop;
- modify product code;
- create or promote candidates;
- provide a state machine or evaluator runtime;
- merge branches;
- deploy artifacts;
- allow a builder to certify its own work.

YAML input requires PyYAML to be importable. JSON validation and the vendored runtime remain
standard-library-only.

### Reproduce

```bash
uv lock --check
uv sync --frozen --all-groups
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest
uv build
uv run python scripts/render_vendor_bundle.py \
  --target build/vendor/_vendor_loop_schemas \
  --source-commit "$(git rev-parse HEAD)"
uv run python scripts/render_vendor_bundle.py \
  --target build/vendor/_vendor_loop_schemas \
  --source-commit "$(git rev-parse HEAD)" \
  --check
```
