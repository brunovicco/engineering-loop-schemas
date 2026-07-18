# engineering-loop-schemas

Canonical, shared schemas and a dependency-free validator for Evidence-Gated
Engineering Loops -- the report-only self-improvement workflow shared by the
[Codex](https://github.com/brunovicco/codex-python-engineering-harness) and
[Claude Code](https://github.com/brunovicco/claude-python-engineering-harness)
Python engineering harnesses.

This repository is the embryo of the future unified "alicerce" harness's
loop layer: it is intentionally the *only* new repository created during the
Sprint 0 / Phase 0-1 hardening pass, so that both sibling harnesses can
depend on one source of truth for the loop contract instead of drifting
copies. See `docs/LOOPS.md` in each harness for how it is consumed.

## Non-negotiable principles (Phase 0-1 scope)

- **A builder never certifies its own result.** A `builder-result` document
  is the builder's own, non-authoritative account (see
  `schemas/builder-result.schema.json`). Only a `verdict`, mechanically
  derived from grading `evidence` against a `contract`'s
  `acceptance.hard_gates`, can say PASS.
- **A hard gate is default-FAIL and script-verifiable.** If a gate cannot be
  reduced to a command with an exit code, it is not a hard gate.
- **Evidence is bound to exact commits.** Every `evidence` document carries
  `baseline_sha` and `candidate_sha`, plus a hashed environment
  (`uv_lock_sha256`) and hashed command output, so a verdict can always be
  traced back to exactly what ran against exactly what code.
- **Hooks are defense in depth, not orchestration.** Nothing in this
  repository, or in the Phase 0 integration described in each harness's
  `docs/LOOPS.md`, runs a loop, promotes a candidate, or grants autonomy
  above `report`.
- **This is Phase 0-1: report-only.** No `loop_runner.py`, `loop_gate.py`,
  `loop_state.py`, evaluator, or state machine exists yet, here or in either
  harness. That is out of scope for this sprint by design.

## Layout

```
schemas/
  contract.schema.json        # what a loop run is allowed to do
  evidence.schema.json        # what mechanically happened, hashed and SHA-bound
  verdict.schema.json         # the single PASS/NEEDS_WORK/ESCALATE outcome
  builder-result.schema.json  # a builder's own non-authoritative report
src/loop_schemas/
  models.py                   # stdlib-only dataclasses matching the schemas
  validate_contract.py        # stdlib-only CLI + library contract validator
examples/
  harness-self-improvement.yaml  # a representative, schema-valid contract
tests/
```

## The three-tier model and final states

Every loop run belongs to one of three levels of scrutiny:

1. **Agent-level** -- a single builder attempt against one contract.
2. **Completion-level** -- one full run: builder attempt(s), evidence
   collection, and a verdict.
3. **Operational-level** -- the loop's own health across many runs (budget
   burn, escalation rate, drift between contract and reality).

Every completed run resolves to exactly one final state, recorded on its
`verdict.final_state`:

| State | Meaning |
| --- | --- |
| `SUCCEEDED` | All hard gates passed; candidate is promotable pending human review. |
| `NO_OP` | The builder correctly determined there was nothing to do. |
| `NO_PROGRESS` | The builder produced a candidate, but it does not improve on baseline. |
| `VERIFY_FAILED` | One or more hard gates failed against the candidate. |
| `POLICY_BLOCKED` | The candidate touched `scope.denylist` or an `actions.denied` entry. |
| `BUDGET_EXCEEDED` | `budgets` (tokens, cost, wall clock, or command count) was exceeded. |
| `ESCALATED` | The run could not resolve PASS/FAIL and needs a human decision. |
| `INFRA_FAILED` | The run failed for reasons unrelated to the candidate (tooling, network, environment). |

## Validating a contract

```bash
uv sync
uv run python -m loop_schemas.validate_contract examples/harness-self-improvement.yaml
```

`validate_contract.validate(data: dict) -> list[str]` is also usable as a
library call; an empty list means the contract is valid. Beyond JSON-Schema
structural validation, it additionally checks that `scope.allowlist` and
`scope.denylist` do not literally overlap, that every glob is syntactically
well-formed, that every budget is strictly positive, and that every
`acceptance.hard_gates` entry is one of the named checks a harness's own
`quality_gate.py` can actually run (`lock`, `lint`, `format`, `typing`,
`tests`, `security`, `dependencies`, `architecture`, `mcp`, `governance`).

## Vendoring into a harness

Because `template/scripts/quality_gate.py` in both harnesses must not gain a
new third-party dependency, `src/loop_schemas/models.py` and
`src/loop_schemas/validate_contract.py` are stdlib-only by design (YAML
input degrades gracefully with a clear error if PyYAML is not installed;
JSON input always works with no extra dependency). Until this repository has
a published tag, harnesses vendor these two files verbatim with a header
comment recording the source commit and version, for example:

```python
# Vendored from brunovicco/engineering-loop-schemas @ <commit-sha>
# (no published tag yet as of this vendoring). Do not edit by hand;
# re-vendor from the source repository instead.
```

`models.py` also needs the consuming project's own `pyproject.toml` to carry a matching
`[tool.ruff.lint.per-file-ignores]` entry suppressing `UP037` for wherever the file lands
(e.g. `"scripts/_vendor_loop_schemas/models.py" = ["UP037"]`). Do not add an inline
`# noqa: UP037` instead -- it triggers a `RUF100` unused-directive error on Python
3.12/3.13, where `UP037` never fires (see this repo's CHANGELOG `[Unreleased]` entry).

## Development

```bash
uv sync
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run pyright
```

Coverage is enforced at >=80% (`--cov-fail-under=80` in `pyproject.toml`).
