# engineering-loop-schemas

*[English](README.md)*

Schemas canônicos e compartilhados, com validação JSON sem dependências e suporte
opcional a PyYAML, para Evidence-Gated Engineering Loops -- o workflow de
autoaperfeiçoamento somente-relatório (report-only) compartilhado pelos harnesses
Python de [Codex](https://github.com/brunovicco/codex-python-engineering-harness) e
[Claude Code](https://github.com/brunovicco/claude-python-engineering-harness).

Este repositório é o embrião da camada de loop do futuro harness unificado
("alicerce"): ele é intencionalmente o *único* repositório novo criado durante o
hardening do Sprint 0 / Fase 0-1, para que os dois harnesses irmãos dependam de uma
única fonte de verdade para o contrato de loop, em vez de cópias divergentes. Veja o
`docs/LOOPS.md` de cada harness (também disponível em português como
`docs/LOOPS.pt-BR.md`) para entender como ele é consumido.

## Princípios não negociáveis (escopo da Fase 0-1)

- **Um builder nunca certifica o próprio resultado.** Um documento
  `builder-result` é o relato próprio e não-autoritativo do builder (veja
  `schemas/builder-result.schema.json`). Apenas um `verdict`, derivado
  mecanicamente da avaliação de `evidence` contra os `acceptance.hard_gates` de um
  `contract`, pode dizer PASS.
- **Um hard gate é default-FAIL e verificável por script.** Se um gate não pode
  ser reduzido a um comando com código de saída, ele não é um hard gate.
- **A evidência é vinculada a commits exatos.** Todo documento `evidence` carrega
  `baseline_sha` e `candidate_sha`, além de um ambiente com hash
  (`uv_lock_sha256`). Cada resultado de comando registra terminação tipada,
  hashes de ambos os fluxos de saída e o hash da especificação imutável do gate
  confiável, de modo que um veredito sempre possa ser rastreado até exatamente o
  que rodou contra exatamente qual código e política.
- **Hooks são defesa em profundidade, não orquestração.** Nada neste repositório,
  nem na integração da Fase 0 descrita no `docs/LOOPS.md` de cada harness, executa
  um loop, promove um candidato ou concede autonomia acima de `report`.
- **Isto é a Fase 0-1: somente relatório.** Não existe `loop_runner.py`,
  `loop_gate.py`, `loop_state.py`, avaliador ou máquina de estados, nem aqui nem em
  nenhum dos harnesses. Isso está fora do escopo deste sprint, por design.

## Layout

```
schemas/
  contract.schema.json        # o que uma execução de loop pode fazer
  evidence.schema.json        # o que mecanicamente aconteceu, com hash e vinculado a SHAs
  verdict.schema.json         # o desfecho único PASS/NEEDS_WORK/ESCALATE
  builder-result.schema.json  # o relato próprio e não-autoritativo de um builder
src/loop_schemas/
  models.py                   # dataclasses somente-stdlib espelhando os schemas
  validate_contract.py        # validador de contrato somente-stdlib (CLI + biblioteca)
examples/
  harness-self-improvement.yaml  # um contrato representativo e válido pelos schemas
tests/
```

## O modelo de três níveis e os estados finais

Toda execução de loop pertence a um de três níveis de escrutínio:

1. **Nível do agente (agent-level)** -- uma única tentativa do builder contra um
   contrato.
2. **Nível de conclusão (completion-level)** -- uma execução completa:
   tentativa(s) do builder, coleta de evidência e um veredito.
3. **Nível operacional (operational-level)** -- a saúde do próprio loop ao longo
   de muitas execuções (consumo de budget, taxa de escalonamento, divergência
   entre contrato e realidade).

Toda execução concluída se resolve em exatamente um estado final, registrado em
`verdict.final_state`:

| Estado | Significado |
| --- | --- |
| `SUCCEEDED` | Todos os hard gates passaram; candidato é promovível, pendente de revisão humana. |
| `NO_OP` | O builder determinou corretamente que não havia nada a fazer. |
| `NO_PROGRESS` | O builder produziu um candidato, mas ele não melhora em relação ao baseline. |
| `VERIFY_FAILED` | Um ou mais hard gates falharam contra o candidato. |
| `POLICY_BLOCKED` | O candidato tocou `scope.denylist` ou uma entrada de `actions.denied`. |
| `BUDGET_EXCEEDED` | `budgets` (tokens, custo, tempo de parede ou contagem de comandos) foi excedido. |
| `ESCALATED` | A execução não conseguiu resolver PASS/FAIL e precisa de uma decisão humana. |
| `INFRA_FAILED` | A execução falhou por razões não relacionadas ao candidato (ferramental, rede, ambiente). |

`NO_PROGRESS` é, especificamente, uma constatação confiável de que um candidato não
melhora em relação ao baseline. Diffs equivalentes repetidos ou assinaturas de falha
repetidas são sinais internos de estagnação (stall), não estados finais por si sós.
Sua classificação final segue a causa tipada: por exemplo, falhas de verificação do
candidato, de política, de budget e de infraestrutura permanecem `VERIFY_FAILED`,
`POLICY_BLOCKED`, `BUDGET_EXCEEDED` e `INFRA_FAILED`, respectivamente. Veja o
[`ADR 0001`](docs/adr/0001-no-progress-and-stall-signals.md).

## Validando um contrato

```bash
uv sync
uv run python -m loop_schemas.validate_contract examples/harness-self-improvement.yaml
```

`validate_contract.validate(data: dict) -> list[str]` também pode ser usado como
chamada de biblioteca; uma lista vazia significa que o contrato é válido. Além da
validação estrutural por JSON-Schema, ele verifica adicionalmente que
`scope.allowlist` e `scope.denylist` não se sobrepõem literalmente, que todo glob é
sintaticamente bem formado, que todo budget é estritamente positivo, e que toda
entrada de `acceptance.hard_gates` é uma das verificações nomeadas endereçáveis por
contrato que o próprio `quality_gate.py` de um harness consegue de fato executar
(`lock`, `lint`, `format`, `typing`, `tests`, `security`, `dependencies`,
`architecture`, `mcp`, `governance`).

## Vendorizando em um harness

Como o `template/scripts/quality_gate.py` dos dois harnesses não pode ganhar uma
nova dependência de terceiros, `src/loop_schemas/models.py` e
`src/loop_schemas/validate_contract.py` são somente-stdlib por design (entrada YAML
degrada graciosamente com um erro claro se o PyYAML não estiver instalado; entrada
JSON sempre funciona sem dependência extra).

Os harnesses consomem um bundle determinístico renderizado por
`scripts/render_vendor_bundle.py` a partir da fonte publicada `v0.1.2`. O
renderizador registra em `manifest.json` o commit completo de origem, versão,
repositório, tamanhos de arquivo, hashes SHA-256 e as adaptações declaradas. Os
consumidores atuais estão fixados em `0459d61b7b1d4e7b46709e6d3895770553e6fab0`.

O bundle não é uma cópia byte a byte: o renderizador troca o import de pacote em
`validate_contract.py` de `loop_schemas` para `_vendor_loop_schemas`. Essa única
adaptação está declarada no manifesto e coberta por testes de determinismo,
integridade e adulteração. Não edite um bundle renderizado à mão. Corrija o
repositório de origem, publique uma nova versão e tag, e então renderize um novo
bundle para cada consumidor.

`models.py` também exige que o `pyproject.toml` do projeto consumidor carregue uma
entrada correspondente em `[tool.ruff.lint.per-file-ignores]` suprimindo `UP037`
para onde quer que o arquivo seja colocado (por exemplo,
`"scripts/_vendor_loop_schemas/models.py" = ["UP037"]`). Não use um
`# noqa: UP037` inline no lugar -- ele dispara um erro `RUF100` (diretiva não
utilizada) no Python 3.12/3.13, onde `UP037` nunca é acionado (veja a entrada
`[Unreleased]` do CHANGELOG deste repositório).

## Desenvolvimento

```bash
uv sync
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run pyright
```

A cobertura é exigida em >=80% (`--cov-fail-under=80` no `pyproject.toml`).

