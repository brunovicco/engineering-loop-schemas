# Changelog

All notable changes to this repository are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
