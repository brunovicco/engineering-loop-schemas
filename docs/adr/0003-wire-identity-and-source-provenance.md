# ADR 0003: Separate wire identity and authenticate bundle provenance

- Status: Accepted
- Date: 2026-07-23

## Context

The package release and every serialized document previously carried unrelated
semver values without a defined relationship. Schemas accepted any semver, so
a consumer could not determine which wire format it had received.

The vendor manifest also recorded a caller-supplied repository, version, and
commit but did not prove that those values described the rendered bytes. A
modified working tree could therefore produce a deterministic bundle with
false provenance.

Trusted evidence had the same class of ambiguity: abbreviated commit IDs,
implicit repository and policy identity, and a command display string did not
fully identify the execution graded by a verdict.

## Decision

Document wire versions are independent of package releases and are enforced by
`const` in each JSON Schema.

- contract and builder-result remain `1.0.0`;
- evidence and verdict advance to `2.0.0`.

Evidence `2.0.0` binds:

- canonical repository identity;
- Git object-ID algorithm and complete baseline/candidate OIDs;
- candidate-tree, contract, and policy SHA-256 digests;
- operating system, architecture, executor image, working directory, and
  sandbox profile;
- a shell-free argv for each command;
- typed termination plus independent stdout, stderr, and gate-specification
  hashes.

Verdict `2.0.0` binds the contract digest and complete candidate OID. Its schema
enforces status/final-state compatibility and prevents `PASS` with a failed
gate. Cross-document validation enforces the exact contract gate set.

The vendor renderer now verifies that:

- the version equals `pyproject.toml`;
- the commit equals `HEAD`;
- the repository equals the normalized Git origin;
- the working tree is clean.

It stages the complete target tree, includes all schemas, and hashes every
vendored file in manifest version `2.0.0`.

## Consequences

- Evidence and verdict producers require a breaking migration.
- Consumers can dispatch safely by wire version instead of guessing from a
  package release.
- A source archive without Git identity cannot claim authenticated vendoring;
  render from a clean tagged checkout.
- Full SHA-1 or SHA-256 OIDs are accepted only when they match the declared
  algorithm.
- Repository and policy substitution become detectable from trusted evidence.

## Rejected alternatives

### Use the package version in every document

Rejected because unrelated package fixes would create needless wire-format
versions, while a document format may need compatibility handling independent
of Python distribution releases.

### Keep accepting arbitrary semver

Rejected because syntactic semver validation does not identify a parser or
contract.

### Trust caller-supplied manifest metadata

Rejected because deterministic bytes with unauthenticated labels do not
provide provenance.

### Keep a command display string

Rejected because quoting and shell interpretation make it impossible to prove
the exact process argv from a display string.
