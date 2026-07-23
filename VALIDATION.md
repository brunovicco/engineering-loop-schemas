# Validation record

This document records the validation evidence for `engineering-loop-schemas`
releases. It distinguishes:

- results observed in the local release-candidate quality gate;
- invariants exercised by automated tests;
- evidence that can only be produced from the immutable tagged commit.

Passing the local quality gate does not by itself claim that a GitHub release,
SBOM, checksum set, provenance attestation, or package publication exists.

## `v0.3.0` release-candidate validation

Validated on 2026-07-23 for the breaking `v0.3.0` release candidate.

### Release identity

| Item | Value |
| --- | --- |
| Package | `loop-schemas` |
| Candidate package version | `0.3.0` |
| Previous release | `v0.2.0` |
| Previous release commit | `4c17dfc7b58b0376a297b728b5ef8cae8c2d2bde` |
| Contract wire format | `1.0.0` |
| Builder-result wire format | `1.0.0` |
| Evidence wire format | `2.0.0` |
| Verdict wire format | `2.0.0` |
| Vendor manifest format | `2.0.0` |
| Validation date | `2026-07-23` |

Package release versions and document wire-format versions are independent.
Consumers must select a document parser from the document's `version` field,
not from the installed package version.

The release candidate was validated before creation of its final release
commit and annotated tag. The authoritative release source will be the
immutable commit referenced by `v0.3.0` after promotion. This record therefore
does not embed or claim a final `v0.3.0` commit OID.

### Validation environment

| Component | Observed value |
| --- | --- |
| Operating system | macOS (`darwin`) |
| Python | `3.13.12` |
| pytest | `9.1.1` |
| pytest-cov | `6.0.0` |
| Pyright | `1.1.407` |
| Ruff | `0.15.21` |
| Dependency resolution | `uv.lock`, frozen installation |

Pyright reported that a newer upstream version was available. This was an
informational notice only; the repository intentionally used its pinned
version and completed with zero errors and zero warnings.

### Local quality-gate results

| Check | Result | Evidence |
| --- | --- | --- |
| Lockfile consistency | Passed | `uv lock --check` resolved 19 packages without modifying the lock |
| Frozen dependency installation | Passed | Local package changed from `0.2.0` to `0.3.0` |
| Ruff lint | Passed | `All checks passed!` |
| Ruff format | Passed | 21 files already formatted |
| Pyright strict | Passed | 0 errors, 0 warnings, 0 informations |
| Test collection | Passed | 93 tests collected |
| Test execution | Passed | 93 tests passed in 2.32 seconds |
| Coverage threshold | Passed | 92.04%, above the enforced 90% minimum |
| Source distribution build | Passed | `dist/loop_schemas-0.3.0.tar.gz` |
| Wheel build | Passed | `dist/loop_schemas-0.3.0-py3-none-any.whl` |
| Whitespace/error-marker check | Passed | `git diff --check` completed without output |

### Test-suite results

| Test module | Tests | Result |
| --- | ---: | --- |
| `tests/test_cli.py` | 3 | Passed |
| `tests/test_contract_validation.py` | 15 | Passed |
| `tests/test_evidence_command_integrity.py` | 13 | Passed |
| `tests/test_example_contract.py` | 3 | Passed |
| `tests/test_models_match_schemas.py` | 4 | Passed |
| `tests/test_package_artifacts.py` | 2 | Passed |
| `tests/test_package_version.py` | 1 | Passed |
| `tests/test_python314_lint_compatibility.py` | 3 | Passed |
| `tests/test_schemas_are_valid.py` | 5 | Passed |
| `tests/test_stdlib_schema_parity.py` | 23 | Passed |
| `tests/test_vendor_bundle.py` | 13 | Passed |
| `tests/test_verdict_validation.py` | 6 | Passed |
| `tests/test_workflows.py` | 2 | Passed |
| **Total** | **93** | **Passed** |

### Coverage results

| Source | Statements | Missed | Coverage |
| --- | ---: | ---: | ---: |
| `scripts/render_vendor_bundle.py` | 180 | 19 | 89% |
| `src/loop_schemas/__init__.py` | 4 | 0 | 100% |
| `src/loop_schemas/_stdlib_jsonschema.py` | 163 | 10 | 94% |
| `src/loop_schemas/models.py` | 178 | 1 | 99% |
| `src/loop_schemas/schema_resources.py` | 21 | 3 | 86% |
| `src/loop_schemas/validate_contract.py` | 120 | 20 | 83% |
| **Total** | **666** | **53** | **92.04%** |

Coverage includes both the installed package and the vendor-bundle renderer.
The enforced project threshold is 90%.

### Contract and validation guarantees exercised

The test suite exercised the following contract-validation behavior:

- canonical JSON Schema Draft 2020-12 files are valid schemas;
- the standard-library evaluator applies every assertion keyword used by the
  canonical schemas;
- unsupported schema assertion keywords fail closed;
- standard-library validation remains aligned with the `jsonschema` reference
  implementation for the adversarial corpus;
- unknown properties, wrong types, invalid enums, empty required collections,
  duplicate values, and unsupported document versions are rejected;
- unexpected input types produce structured validation errors instead of
  leaking `TypeError`;
- dataclass fields and canonical schema properties remain aligned;
- the example contract passes both schema and domain validation;
- the report-only contract invariants and supported hard-gate vocabulary are
  enforced;
- Python 3.12, 3.13, and 3.14 Ruff target-version compatibility is covered by
  the regression suite.

### Evidence and verdict guarantees exercised

The test suite exercised the following trusted-document behavior:

- evidence uses complete Git object IDs with an explicit object-ID algorithm;
- evidence binds repository identity, baseline and candidate OIDs, candidate
  tree, contract, policy, and executor context;
- trusted commands are represented as shell-free `argv` arrays;
- termination and exit-code combinations are closed and internally
  consistent;
- stdout, stderr, and trusted gate specifications have independent SHA-256
  bindings;
- verdicts bind the candidate OID, contract hash, and evidence hash;
- verdict `status` and `final_state` combinations are constrained;
- a `PASS` verdict cannot contain a failed gate;
- duplicate, missing, and undeclared gate results are rejected when validating
  a verdict against its contract;
- evidence and verdict wire versions are fixed at `2.0.0`.

### Package artifact guarantees exercised

The package-artifact tests verified that the built wheel contains:

- the public model and document-version API;
- `load_schema()` and `schema_text()`;
- the fail-closed standard-library structural evaluator;
- the schema resource loader;
- the document validator;
- `contract.schema.json`;
- `builder-result.schema.json`;
- `evidence.schema.json`;
- `verdict.schema.json`.

The successful build produced:

```text
dist/loop_schemas-0.3.0.tar.gz
dist/loop_schemas-0.3.0-py3-none-any.whl
```

Artifact SHA-256 values are intentionally not recorded here because the
tag-triggered release-evidence workflow is responsible for rebuilding the
distributions from the immutable release commit and generating the
authoritative checksum set.

### Vendor-bundle guarantees exercised

The vendor-bundle tests verified:

- deterministic rendering;
- complete drift detection;
- staged replacement of the complete target tree;
- rejection of unexpected files, symlinks, and content tampering;
- verification of the declared package version;
- verification that the requested source commit equals Git `HEAD`;
- verification of the canonical source repository;
- rejection of dirty working trees;
- inclusion of Python sources and all canonical schemas;
- SHA-256 and byte-size binding for every vendored file;
- explicit recording of package-import adaptations.

Vendor manifest `2.0.0` covers:

```text
__init__.py
_stdlib_jsonschema.py
models.py
schema_resources.py
validate_contract.py
schemas/builder-result.schema.json
schemas/contract.schema.json
schemas/evidence.schema.json
schemas/verdict.schema.json
manifest.json
```

The automated tests establish renderer behavior. A bundle claiming the actual
`v0.3.0` source commit must still be rendered from a clean checkout of the
final tagged commit.

### Release-evidence workflow status

| Evidence | Local candidate | Required release source |
| --- | --- | --- |
| Unit and integration tests | Passed | Release PR CI |
| Coverage threshold | Passed | Release PR CI |
| Python 3.12-3.14 matrix | Not claimed by this local run | GitHub Actions |
| Distribution build | Passed locally | Tagged commit workflow |
| Distribution checksums | Not yet produced | Tagged commit workflow |
| SPDX JSON SBOM | Not yet produced | Tagged commit workflow |
| Build provenance attestation | Not yet produced | Tagged commit workflow |
| SBOM attestation | Not yet produced | Tagged commit workflow |
| GitHub Release | Not yet created | Explicit post-workflow promotion |
| PyPI publication | Out of scope for this workflow | Separate explicit action |

The release-evidence workflow is tag-gated and uses actions pinned to complete
commit SHAs. It preserves generated evidence as workflow artifacts and does not
publish the package or create a GitHub Release automatically.

### Scope and limitations

`engineering-loop-schemas` remains report-only. It defines and validates
contracts, trusted evidence, trusted verdicts, and non-authoritative builder
results. It does not:

- execute an engineering loop;
- modify product code;
- create or promote candidates;
- provide an evaluator runtime or state machine;
- merge branches or deploy artifacts;
- collect trusted evidence on behalf of an executor;
- allow a builder to certify its own work.

JSON validation requires only the Python standard library. YAML input requires
PyYAML. RFC 8785/JCS serialization and hashing remain producer
responsibilities: the package defines required digest bindings but does not
collect or reconstruct authoritative bytes.

### Reproduce the local quality gate

From the repository root:

```bash
uv lock --check
uv sync --frozen --all-groups
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest
uv build
git diff --check
```

Confirm the installed package version:

```bash
uv run python -c 'import loop_schemas; print(loop_schemas.__version__)'
```

Expected output:

```text
0.3.0
```

### Verify release provenance after the release commit

The renderer requires a clean tree. After committing the release changes:

```bash
release_commit="$(git rev-parse HEAD)"
release_tmp="$(mktemp -d)"

uv run python scripts/render_vendor_bundle.py \
  --target "$release_tmp/_vendor_loop_schemas" \
  --source-commit "$release_commit"

uv run python scripts/render_vendor_bundle.py \
  --target "$release_tmp/_vendor_loop_schemas" \
  --source-commit "$release_commit" \
  --check

git status --short
```

The final command must produce no output. Untracked files, including local
operating-system metadata, must be removed or ignored before this check.

After the release PR is merged, repeat the provenance check from the exact
`main` commit that will receive the annotated `v0.3.0` tag.

### Promotion requirements

Before creating `v0.3.0`:

1. Merge the release-only PR after all required checks pass.
2. Update a local `main` with `git pull --ff-only`.
3. Confirm that the working tree is clean.
4. Repeat the vendor provenance render and `--check` against the exact merge
   commit.
5. Create and push the annotated `v0.3.0` tag on that commit.
6. Verify the tag-triggered quality gate and release-evidence workflow.
7. Download and review the distributions, checksum set, SPDX SBOM, provenance
   attestation, and SBOM attestation.
8. Create the GitHub Release only after all evidence is consistent with the
   tagged commit.
9. Re-render downstream vendor bundles from the clean, tagged release source.

## Published baseline — `v0.2.0`

The previous published release is
[`v0.2.0`](https://github.com/brunovicco/engineering-loop-schemas/releases/tag/v0.2.0),
from commit `4c17dfc7b58b0376a297b728b5ef8cae8c2d2bde`.

`v0.2.0` predates:

- canonical-schema enforcement by the standard-library validator;
- installed schema resources;
- evidence and verdict wire format `2.0.0`;
- complete source and document identity bindings;
- authenticated vendor source-provenance checks;
- release SBOM and attestation workflow support.
