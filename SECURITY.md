# Security policy

This repository distributes the canonical contract, evidence, verdict, and builder-result schemas
plus a stdlib-only validator consumed - as a pinned, hash-verified vendor bundle - by
`codex-python-engineering-harness` and `claude-python-engineering-harness`. A flaw here can
propagate to every project those harnesses generate.

## Supported versions

Security fixes are provided for the latest tagged release on the default branch. Consumers pin
the bundle by version and full commit; upgrade to the fixed release and re-render the bundle.

## What is in scope

- Validator flaws that accept a contract, evidence, or verdict document violating the schemas,
  or that allow a builder-result to be treated as authoritative.
- Schema changes or ambiguities that would let a hard gate pass by default or without a
  command-with-exit-code reduction.
- Vendor-bundle rendering flaws that produce nondeterministic output or bypass the recorded
  SHA-256 integrity hashes.
- Path traversal, unsafe deserialization, or code execution in `validate_contract.py` or
  `render_vendor_bundle.py`.

## What is out of scope

- Vulnerabilities in the consuming harnesses; report them to the affected harness repository.
- Third-party dependency vulnerabilities in a consumer's environment (the core is stdlib-only).
- Findings that require an operator to have modified a vendored bundle by hand.

## Reporting a vulnerability

- Prefer GitHub's private vulnerability reporting: open the repository's **Security** tab and
  choose **Report a vulnerability**.
- If that option is unavailable, email **bfvicco@gmail.com** with the subject
  `[SECURITY] engineering-loop-schemas`. Do not include production secrets or personal data that
  are not needed to reproduce the issue.

Please do not open a public issue for a suspected vulnerability before the maintainers have had a
chance to assess and, where warranted, ship a fix. You should receive an acknowledgement within
five business days. Coordinate public disclosure with the maintainer.
