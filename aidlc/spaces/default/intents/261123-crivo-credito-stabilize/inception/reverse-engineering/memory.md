# Reverse Engineering — Memory

> **Stage**: reverse-engineering | **Phase**: inception | **Intent**: 261123-crivo-credito-stabilize
> **Date**: 2026-11-23 | **Agent**: Polaris (PM)

---

## Observações

Projeto brownfield com código funcional existente. Reverse engineering focado em documentar decisões já implementadas como baseline (ADRs 001-007), não em descobrir requisitos novos.

### Código Analisado
- **crivo/engine.py**: Motor determinístico, 3 regras, política versionada
- **crivo/service.py**: Orquestração, Event Sourcing, adapters injetáveis, human-in-the-loop
- **crivo/server.py**: HTTP server nativo, origin validation, rotas API + UI
- **crivo/hermes.py**: Adapter Hermes opt-in, cliente HTTP gateway local
- **crivo/run_server.py**: Entry point com sys.path fix
- **index.html**: UI single-page vanilla JS + fetch API
- **demo.py, verify.py, test_origin_regression.py**: Scripts de teste/demo

### Decisões Baseline Extraídas (→ ADRs 001-007)
1. Stack Python stdlib + SQLite (zero deps)
2. Arquitetura 4 camadas com DI
3. Motor determinístico versionado imutável
4. Event Sourcing para auditoria
5. Human-in-the-loop obrigatório
6. Security-first: loopback + origin validation + CSRF
7. Dois modos execução: simulado/hermes via DI

### Gaps Identificados (→ Pendências Inception)
- Sem CI/CD
- Testes customizados (não pytest/unittest)
- Sem requirements.txt/pyproject.toml
- Sem linter/formatter/type checker
- Binários/segredos no repo (já comittados)

---

## Tradeoffs

| Decisão | Tradeoff | Racional |
|---------|----------|----------|
| Python stdlib only | Sem framework web, validação manual | POC simples, zero deps, portável |
| SQLite embarcado | Sem servidor DB, single-file | Demo local, sem infra |
| Event Sourcing em SQLite | Mais storage, queries complexas | Auditoria completa, rastreabilidade |
| Human-in-the-loop sempre | Latência, não escalável | Compliance, segurança, regulatório |
| Dois modos via DI | Duplicação lógica parecer | Flexibilidade, out-of-the-box + opt-in LLM |

---

## Desvios (Deviations)

Nenhum desvio de padrões AI-DLC — projeto brownfield segue workflow Baseline → Integrate → Validate.

---

## Perguntas Abertas

1. **CI/CD**: Qual plataforma? GitHub Actions (repo no GitHub) vs GitLab CI vs outro?
2. **Testes**: Migrar para pytest? Manter scripts customizados para testes de integração Hermes?
3. **Dependências**: Adicionar pyproject.toml com dependências opcionais (pytest, ruff, mypy)?
4. **Binários no repo**: Manter cloudflared/password no histórico? (já público, não removível)
5. **Modo Hermes**: Validar modelo no gateway? Assinatura de resposta para auditabilidade?

---

## Próximos Passos

1. Aguardar aprovação Gate 2 (Baseline → Integrate) — Rodrigo (PM)
2. Executar Integrate workflow (criar estrutura aidlc/ completa)
3. Iniciar requirements-analysis (stage 1.2) após Gate 3

---

*Reverse engineering baseline completo. ADRs 001-007 criados como Implemented. ADRs 008-012 propostos para governança AI-DLC.*