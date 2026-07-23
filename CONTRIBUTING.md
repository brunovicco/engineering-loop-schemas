# Contributing

> **Report-only boundary.** Schema and validation changes are welcome when they strengthen the
> trust boundary, but breaking wire changes require a migration guide, a minor package release,
> and coordinated consumer updates. Loop-runner functionality remains out of scope.

This repository is the canonical source for the Evidence-Gated Engineering Loop schemas. Both
sibling harnesses consume it as a pinned, hash-verified vendor bundle, so every change here can
propagate to every project either harness generates. Treat changes accordingly.

Before contributing, read `SUPPORT.md` and `CODE_OF_CONDUCT.md`. Report suspected vulnerabilities
privately as described in `SECURITY.md`.

## Local checks

```bash
uv sync --all-groups
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest
uv build
uv run python -m loop_schemas.validate_contract examples/harness-self-improvement.yaml
```

The test suite enforces model/schema parity, differential validator behavior, valid examples,
wheel contents, verdict consistency, deterministic vendoring, source provenance, and lint
compatibility across Python 3.12-3.14.

## Design constraints

- `models.py` and `validate_contract.py` are stdlib-only. PyYAML is optional and only for YAML
  contracts; JSON must always work with no dependency.
- Do not use `from __future__ import annotations`; quote an individual forward reference only
  when evaluation order requires it.
- A builder-result document is never authoritative. Do not add fields that would let a builder
  certify its own outcome.
- Hard gates must reduce to a command with an exit code; do not add prose-judged gates.
- Every document schema uses `const` for its wire version. Do not couple a wire version to the
  Python package version.
- Adding a schema assertion keyword requires stdlib evaluator support and a differential test in
  the same change. Unknown assertion keywords must remain fail-closed.

## Language policy

English is the canonical language for all documentation. `README.md` also ships a
`README.pt-BR.md` sibling, updated in the same change; no other translations are maintained here.
The conceptual loop documentation is translated in each consuming harness
(`docs/LOOPS.pt-BR.md`), which is the natural pt-BR entry point.

## Releasing

Schema changes require a new version tag (`vX.Y.Z`), a `CHANGELOG.md` entry, an updated
`MIGRATION.md` for breaking changes, and a re-rendered vendor bundle consumed by every downstream
project. Render from a clean checkout of the tagged full commit. Never edit a vendored copy in a
consumer directly.

The tag must exactly match `project.version`. The tag-triggered release-evidence workflow builds
the distributions, generates checksums and an SPDX SBOM, and creates provenance and SBOM
attestations. It deliberately does not publish; inspect that evidence before creating a release or
uploading to a package index.
