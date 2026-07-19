# Support policy

This project is maintained on a best-effort basis. It does not provide a service-level agreement,
guaranteed response time, or consulting through public issues.

## Supported requests

Open a GitHub issue for:

- reproducible defects in the schemas, models, validator, or vendor-bundle renderer;
- divergence between `schemas/*.json` and `src/loop_schemas/models.py`;
- documentation that is incorrect or prevents successful evaluation;
- compatibility problems with the supported Python versions (3.12-3.14).

Include a minimal reproduction, version or commit, environment details, and sanitized output.

## Feature requests

The Phase 0-1 core is in feature freeze (see `CONTRIBUTING.md`). Proposals for new schema fields,
document types, or loop-runner functionality will be recorded but not implemented until the next
phase is approved. Harness-specific behavior belongs in the consuming harness repositories.

## Questions and troubleshooting

Review `README.md`, `VALIDATION.md`, and each harness's `docs/LOOPS.md` before opening an issue.
Usage questions without a reproducible problem may be closed or converted into documentation
suggestions.

## Security and conduct

Do not report suspected vulnerabilities in public issues. Follow `SECURITY.md` for private
reporting. Participation in issues, pull requests, and other project spaces is governed by
`CODE_OF_CONDUCT.md`.

## Support window

Only the latest tagged release and the default branch receive fixes. Vendored bundles in consumer
repositories are owned by those repositories and are updated by re-rendering, never patched in
place.
