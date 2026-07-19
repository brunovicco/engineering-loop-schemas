# Contributing

> **Feature freeze.** The Phase 0-1 schema core is intentionally frozen while both consuming
> harnesses (`codex-python-engineering-harness` and `claude-python-engineering-harness`) integrate
> it. Bug fixes, security fixes, and documentation corrections are welcome; new schema fields,
> new document types, or loop-runner functionality are out of scope until the next phase is
> approved.

This repository is the canonical source for the Evidence-Gated Engineering Loop schemas. Both
sibling harnesses consume it as a pinned, hash-verified vendor bundle, so every change here can
propagate to every project either harness generates. Treat changes accordingly.

Before contributing, read `SUPPORT.md` and `CODE_OF_CONDUCT.md`. Report suspected vulnerabilities
privately as described in `SECURITY.md`.

## Local checks

```bash
uv sync --all-groups
uv run pytest
uv run python -m loop_schemas.validate_contract examples/harness-self-improvement.yaml
```

The test suite enforces that `src/loop_schemas/models.py` stays in sync with `schemas/*.json`,
that the example contract validates, that the rendered vendor bundle is deterministic, and that
the source stays lint-compatible with Python 3.12-3.14.

## Design constraints

- `models.py` and `validate_contract.py` are stdlib-only. PyYAML is optional and only for YAML
  contracts; JSON must always work with no dependency.
- Do not use `from __future__ import annotations`; quote an individual forward reference only
  when evaluation order requires it.
- A builder-result document is never authoritative. Do not add fields that would let a builder
  certify its own outcome.
- Hard gates must reduce to a command with an exit code; do not add prose-judged gates.

## Language policy

English is the canonical language for all documentation. `README.md` also ships a
`README.pt-BR.md` sibling, updated in the same change; no other translations are maintained here.
The conceptual loop documentation is translated in each consuming harness
(`docs/LOOPS.pt-BR.md`), which is the natural pt-BR entry point.

## Releasing

Schema changes require a new version tag (`vX.Y.Z`), a `CHANGELOG.md` entry, and a re-rendered
vendor bundle (`scripts/render_vendor_bundle.py`) consumed by both harnesses in a follow-up
change. Never edit a vendored copy in a harness directly.
