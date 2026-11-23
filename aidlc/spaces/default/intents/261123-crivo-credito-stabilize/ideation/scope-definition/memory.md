# Ideation Scope Definition — Memory (SKIPPED — Brownfield)

> **Stage**: scope-definition | **Phase**: ideation | **Intent**: 261123-crivo-credito-stabilize
> **Date**: 2026-11-23 | **Agent**: Polaris (PM)
> **Status**: SKIPPED — Projeto brownfield com escopo definido

---

## Escopo Definido (do Diagnose/Plan)

### In Scope — AI-DLC Integration Only
- Workspace `aidlc/` structure completa
- Baseline histórico (ADRs 001-007 `Implemented`)
- Governança AI-DLC (ADRs 008-012 `Proposed`)
- Stage gates 0-4 com aprovação Rodrigo (PM)
- Integração Agentic-Home (skills, templates, catálogo)
- Handoff.md estendido AI-DLC
- Validação: recuperação contexto, idempotência, rollback, gates

### Out of Scope — Preservar Existente
- Código funcional `crivo/` (100% preservado)
- Histórico Git (6 commits, branch main)
- README.md, AGENTS.md (apenas adição seção AI-DLC)
- Binários/segredos no repo (documentados, não removidos)
- Modos de execução simulado/hermes (preservados)

---

## Critérios de Escopo
| Critério | Decisão |
|----------|---------|
| Tipo projeto | Brownfield integration |
| Preservação código | 100% — nenhum arquivo funcional modificado |
| Histórico Git | Imutável — tags para checkpoints |
| Aprovações | Humanas obrigatórias (Rodrigo PM Gates 0-4) |
| Integração Home | Skills + templates + catálogo + governança |

---

## Próximos Passos
*Ver intent-capture memory*

---

*Scope definition SKIPPED — escopo já definido no Diagnose/Plan.*