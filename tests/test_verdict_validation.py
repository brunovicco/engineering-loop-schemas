"""Verdict consistency and cross-document gate completeness."""

import copy

from loop_schemas.validate_contract import validate_verdict

from .test_stdlib_schema_parity import contract_document, verdict_document


def test_matching_verdict_and_contract_are_valid() -> None:
    assert validate_verdict(verdict_document(), contract=contract_document()) == []


def test_pass_cannot_contain_a_failed_gate() -> None:
    verdict = verdict_document()
    verdict["justification"]["gate_results"][0]["passed"] = False

    errors = validate_verdict(verdict, contract=contract_document())

    assert errors


def test_status_and_final_state_cannot_contradict_each_other() -> None:
    verdict = verdict_document()
    verdict["final_state"] = "VERIFY_FAILED"

    errors = validate_verdict(verdict, contract=contract_document())

    assert errors


def test_duplicate_gate_names_are_rejected_even_when_details_differ() -> None:
    verdict = verdict_document()
    verdict["justification"]["gate_results"].append(
        {"gate": "tests", "passed": True, "detail": "duplicate"}
    )

    errors = validate_verdict(verdict, contract=contract_document())

    assert any("duplicate" in error for error in errors)


def test_gate_results_must_exactly_cover_contract_hard_gates() -> None:
    contract = contract_document()
    contract["acceptance"]["hard_gates"] = ["lint", "tests"]
    verdict = verdict_document()
    verdict["justification"]["gate_results"] = [{"gate": "security", "passed": True}]

    errors = validate_verdict(verdict, contract=contract)

    assert any("missing" in error and "lint" in error and "tests" in error for error in errors)
    assert any("undeclared" in error and "security" in error for error in errors)


def test_verdict_contract_identity_must_match() -> None:
    verdict = copy.deepcopy(verdict_document())
    verdict["contract_id"] = "another-contract"

    errors = validate_verdict(verdict, contract=contract_document())

    assert any("contract_id" in error for error in errors)
