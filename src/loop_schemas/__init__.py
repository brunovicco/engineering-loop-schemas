"""Evidence-Gated Engineering Loop schemas: models and a dependency-free validator.

This package is the canonical, shared contract between every engineering-loop
implementation (currently the Codex and Claude Code Python engineering
harnesses). It defines the shape of a loop `contract`, the mechanical `evidence`
a run produces, the `verdict` derived from grading that evidence, and the
non-authoritative `builder-result` a builder reports.

Everything here is Phase 0-1, report-only: no code in this package executes a
loop, promotes a candidate, or grants any agent the authority to certify its
own work. See README.md for the full model and the documented final states.
"""

from loop_schemas.models import (
    BUILDER_RESULT_DOCUMENT_VERSION,
    CONTRACT_DOCUMENT_VERSION,
    EVIDENCE_DOCUMENT_VERSION,
    FINAL_STATES,
    VERDICT_DOCUMENT_VERSION,
    Acceptance,
    Actions,
    Baseline,
    Budgets,
    BuilderResult,
    CommandResult,
    Confidence,
    Contract,
    Environment,
    Evidence,
    ExecutionTermination,
    FinalState,
    GateResult,
    HumanReview,
    Justification,
    ObjectIdAlgorithm,
    Scope,
    Selection,
    SelfReported,
    TokenUsage,
    Trigger,
    TriggerType,
    Usage,
    Verdict,
    VerdictStatus,
)
from loop_schemas.schema_resources import (
    SCHEMA_FILENAMES,
    DocumentKind,
    load_schema,
    schema_text,
)

__all__ = [
    "Acceptance",
    "Actions",
    "Baseline",
    "BUILDER_RESULT_DOCUMENT_VERSION",
    "BuilderResult",
    "Budgets",
    "CONTRACT_DOCUMENT_VERSION",
    "CommandResult",
    "Confidence",
    "Contract",
    "DocumentKind",
    "EVIDENCE_DOCUMENT_VERSION",
    "Environment",
    "Evidence",
    "ExecutionTermination",
    "FINAL_STATES",
    "FinalState",
    "GateResult",
    "HumanReview",
    "Justification",
    "ObjectIdAlgorithm",
    "SCHEMA_FILENAMES",
    "Scope",
    "Selection",
    "SelfReported",
    "TokenUsage",
    "Trigger",
    "TriggerType",
    "Usage",
    "VERDICT_DOCUMENT_VERSION",
    "Verdict",
    "VerdictStatus",
    "load_schema",
    "schema_text",
]

__version__ = "0.3.0"
