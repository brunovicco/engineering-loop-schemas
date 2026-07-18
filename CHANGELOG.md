# Changelog

All notable changes to this repository are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `LICENSE` (MIT), matching the license already declared in `pyproject.toml`'s `[project]`
  table -- present in both sibling harnesses but missing here since this repo's initial
  commit.

### Fixed

- `models.py`: suppress ruff's `UP037` on the quoted self-referencing `from_dict` return
  annotations (e.g. `-> "Budgets"`) via a targeted `[tool.ruff.lint.per-file-ignores]`
  entry in `pyproject.toml`, not an inline `# noqa: UP037`. The quotes are load-bearing on
  Python 3.12/3.13 -- this module deliberately avoids `from __future__ import annotations`
  so it stays safe to vendor into codebases that ban that import -- and `UP037` incorrectly
  flags them as unnecessary whenever a caller's ruff `target-version` is `py314` (where PEP
  649 lazy annotations are the default). Caught when this file was vendored into a harness
  project rendered for Python 3.14 and failed CI lint. An inline `# noqa: UP037` was tried
  first but caused a *different* failure (`RUF100`, unused-directive) on 3.12/3.13, where
  `UP037` never fires in the first place, so the noqa has nothing to suppress there; the
  per-file-ignore avoids that because it isn't line-scoped. Added a regression test that
  lints `models.py` against every supported target-version (`py312`, `py313`, `py314`).
  Consuming projects need the equivalent per-file-ignore for wherever they vendor this file
  (see README.md's vendoring section).
- `validate_contract.py`: dropped a stray `# noqa: PLC0415` on the lazy `import yaml`. No
  known consumer (this repo or either sibling harness) selects ruff's `PL` rule family, so
  the directive suppressed nothing locally but became a second `RUF100` unused-directive
  failure once vendored into a harness project that enables `RUF` (both harnesses' `library`
  and `workspace` profiles do). Replaced with a plain comment; the import stays function-local
  on purpose (YAML is an optional dependency).

## [0.1.0] - 2026-07-18

Initial release: the canonical Evidence-Gated Engineering Loop contract, established as part of
the Codex/Claude Code Python engineering harness consolidation (Sprint 0, Phase 0-1, report-only).

### Added

- `schemas/contract.schema.json`, `schemas/evidence.schema.json`, `schemas/verdict.schema.json`,
  and `schemas/builder-result.schema.json` (JSON Schema Draft 2020-12).
- `src/loop_schemas/models.py`: stdlib-only dataclasses corresponding to the schemas.
- `src/loop_schemas/validate_contract.py`: stdlib-only CLI and library contract validator,
  checking schema conformance, `scope.allowlist`/`scope.denylist` disjointness, glob syntax,
  positive budgets, and hard-gate membership in the set both sibling harnesses' quality gates
  actually support.
- `examples/harness-self-improvement.yaml`: a representative, schema-valid example contract.
- Test suite: schema self-validation, contract validation behavior, example-contract
  cross-validation against both the JSON Schema and `validate_contract.validate()`, and CLI
  behavior. Coverage enforced at >=80%.

[Unreleased]: https://github.com/brunovicco/engineering-loop-schemas/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/brunovicco/engineering-loop-schemas/releases/tag/v0.1.0
