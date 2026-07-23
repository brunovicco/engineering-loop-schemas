# ADR 0001: NO_PROGRESS and Internal Stall Signals

Status: Accepted
Date: 2026-07-18

## Context

The canonical `NO_PROGRESS` final state in v0.1.2 means that a builder
produced a candidate that does not improve on the baseline. Earlier design
material also used “no progress” informally for repeated equivalent diffs or
failure signatures across attempts.

Those concepts are related but not equivalent. A repeated result can be caused
by candidate quality, a hard-gate failure, policy, exhausted budget,
infrastructure, or an unresolved condition. Mapping every stall directly to
`NO_PROGRESS` would hide the actual cause and weaken final-state semantics.

## Decision

The serialized meaning of `NO_PROGRESS` remains unchanged:

> A candidate exists, but trusted evaluation determines that it does not
> improve on the baseline.

Repeated equivalent diffs, unchanged candidate identities, or repeated failure
signatures are internal stall signals. They are evidence inputs, not canonical
final states and not verdicts by themselves.

The trusted evaluator classifies the run using all authoritative evidence:

- no measurable improvement over baseline may produce `NO_PROGRESS`;
- failed candidate hard gates produce `VERIFY_FAILED`;
- denied scope or actions produce `POLICY_BLOCKED`;
- exhausted contract budgets produce `BUDGET_EXCEEDED`;
- infrastructure-caused repetition produces `INFRA_FAILED`;
- unresolved or unsafe classification produces `ESCALATED`.

A builder cannot declare either stall or `NO_PROGRESS` authoritatively.

## Consequences

- The verdict vocabulary and the meaning of `NO_PROGRESS` do not change.
- Stall detection may evolve inside an evaluator without creating schema drift.
- Equivalent repetition does not erase the typed cause of failure.
- Alicerce may persist stall signals internally but must serialize only the
  canonical final state selected from authoritative evidence.

## Rejected alternatives

### Redefine NO_PROGRESS as any repeated outcome

Rejected because repeated gate, policy, budget, and infrastructure failures have
more precise canonical states.

### Add a STALLED final state immediately

Rejected because no demonstrated serialization requirement justifies a schema
change in Phase 0-1.

### Trust the builder's self-reported progress

Rejected because builder results are explicitly non-authoritative.

## Acceptance conditions

- Documentation distinguishes stall signals from canonical final states.
- Tests continue to require the existing eight-state vocabulary.
- No schema, model, tag, or vendored consumer bundle changes for this decision.
- Future evaluator tests classify repeated outcomes according to their typed
  cause rather than repetition alone.
