# Migration guide

## `v0.2.x` to the next breaking release

The next release is expected to be `v0.3.0`. Package release versions and
document wire-format versions are independent: consumers select a document
parser from the document's `version` field.

### Evidence `1.0.0` to `2.0.0`

| Before | After |
| --- | --- |
| `baseline_sha`, `candidate_sha` accepted 7-40 characters | `oid_algorithm` plus complete `baseline_oid` and `candidate_oid` |
| No repository identity | Required canonical `repository` |
| Contract and policy implied | Required `contract_sha256` and `policy_sha256` |
| Candidate content implied by commit | Required `candidate_tree_sha256` |
| `command` display string | Shell-free `argv` array |
| Python and lock digest only | OS, architecture, image, working directory, and sandbox profile also required |
| Any semver accepted | `version` must equal `2.0.0` |

Producers must calculate hashes from the exact immutable bytes consumed by the
trusted executor. Do not populate hashes from reconstructed or pretty-printed
representations.

### Verdict `1.0.0` to `2.0.0`

- Replace `candidate_sha` with `oid_algorithm` and complete `candidate_oid`.
- Add `contract_sha256`.
- Set `version` to `2.0.0`.
- Ensure `status` and `final_state` use an allowed combination.
- For `PASS`, every gate result must have `passed: true`.
- When a contract is available, provide exactly one gate result for each
  `acceptance.hard_gates` entry and no others.
- Calculate `evidence_sha256` over RFC 8785/JCS canonical JSON bytes.

### Contract and builder result

Their wire version remains `1.0.0`. Validation is stricter:

- arbitrary semver values are no longer accepted;
- unknown properties, wrong types, duplicates, and empty required strings are
  rejected consistently;
- builder Git SHAs must be complete 40-character SHA-1 values;
- a report-only contract must keep `human_review.required: true`.

### Recommended rollout

1. Add readers for both old and new document versions.
2. Upgrade the trusted executor to emit evidence `2.0.0`.
3. Verify the evidence hash and repository/contract/policy bindings.
4. Upgrade the evaluator to emit verdict `2.0.0`.
5. Re-render the vendored bundle from the tagged full commit.
6. Reject legacy writes after every producer is migrated.
7. Remove legacy readers only after retained artifacts have aged out.

Never reinterpret a `1.0.0` document as `2.0.0`; migrate it by rebuilding
trusted evidence from authoritative inputs.
