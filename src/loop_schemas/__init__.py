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
    Acceptance,
    Actions,
    Baseline,
    Budgets,
    Contract,
    HumanReview,
    Scope,
    Selection,
    Trigger,
)

__all__ = [
    "Acceptance",
    "Actions",
    "Baseline",
    "Budgets",
    "Contract",
    "HumanReview",
    "Scope",
    "Selection",
    "Trigger",
]

__version__ = "0.2.0"
