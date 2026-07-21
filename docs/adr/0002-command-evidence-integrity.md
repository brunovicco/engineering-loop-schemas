# ADR 0002: Bind command evidence to typed termination, both output streams, and gate specification

- Status: Proposed
- Date: 2026-07-21

## Context

The existing evidence schema represents an executed command with an integer exit
code and the SHA-256 of stdout. That shape cannot faithfully represent trusted
execution that ends by timeout, cancellation, or output limit. It also leaves
stderr and the immutable gate specification outside the command result.

The Alicerce Phase 2A acceptance criterion A08 requires evidence to bind the
candidate SHA, environment, captured outputs, and gate specification
deterministically. The canonical schema repository must define that contract
before any consumer implements an evidence builder or persistence adapter.

## Decision

\`CommandResult\` records:

- a closed \`termination\` value: \`EXITED\`, \`TIMED_OUT\`, \`CANCELLED\`, or
  \`OUTPUT_LIMIT\`;
- the real integer \`exit_code\` only when termination is \`EXITED\`;
- a null \`exit_code\` for every forced termination;
- independent SHA-256 hashes for stdout and stderr;
- the SHA-256 of the immutable trusted gate specification;
- the command text and duration already present in the contract.

The evidence document continues to bind \`candidate_sha\` and the environment at
the top level. Those fields, together with every command result, are included in
the canonical evidence document later hashed by trusted code.

The JSON Schema rejects contradictory termination and exit-code combinations.
Python dataclasses remain structurally aligned with the language-agnostic
schema. No sentinel exit code is introduced.

## Consequences

This is a breaking evidence-schema change. The next release must be \`v0.2.0\`.
Consumers must not re-pin until that release exists and must migrate producers
to populate every new required field.

The contract can now represent the data needed for A08, but this decision does
not demonstrate A08 by itself. Trusted canonical serialization, hashing,
persistence, candidate verification, and adversarial tampering tests remain
consumer responsibilities.

## Rejected alternatives

- Defining an Alicerce-only evidence model would create a competing canonical
  contract and allow consumers to drift.
- Hashing stdout alone would omit diagnostics that can influence a verdict.
- Encoding timeout or cancellation as conventional exit codes would erase the
  distinction between a process exit and trusted executor intervention.
- Storing a gate name without its specification hash would not bind evidence to
  the policy actually executed.
