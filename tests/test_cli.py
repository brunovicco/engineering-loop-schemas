"""CLI entry point behavior for validate_contract.py."""

from pathlib import Path

from loop_schemas.validate_contract import ContractValidationError, load_document, main


def test_cli_reports_success_for_valid_json_contract(tmp_path: Path, capsys) -> None:
    contract_path = tmp_path / "contract.json"
    contract_path.write_text(
        '{"version":"1.0.0","id":"x","objective":"y",'
        '"trigger":{"type":"manual"},"selection":{"strategy":"s"},'
        '"baseline":{"commands":["true"]},"acceptance":{"hard_gates":["lint"]},'
        '"budgets":{"max_tokens":1},'
        '"scope":{"allowlist":[],"denylist":[]},'
        '"actions":{"allowed":[],"denied":[]},'
        '"human_review":{"required":true}}',
        encoding="utf-8",
    )
    exit_code = main([str(contract_path)])
    assert exit_code == 0
    assert "valid" in capsys.readouterr().out


def test_cli_reports_failure_for_invalid_contract(tmp_path: Path, capsys) -> None:
    contract_path = tmp_path / "contract.json"
    contract_path.write_text("{}", encoding="utf-8")
    exit_code = main([str(contract_path)])
    assert exit_code == 1
    assert "INVALID" in capsys.readouterr().err


def test_load_document_rejects_non_mapping_top_level(tmp_path: Path) -> None:
    contract_path = tmp_path / "contract.json"
    contract_path.write_text("[1, 2, 3]", encoding="utf-8")
    try:
        load_document(contract_path)
    except ContractValidationError as exc:
        assert "mapping" in str(exc)
    else:  # pragma: no cover - defensive
        raise AssertionError("expected ContractValidationError")
