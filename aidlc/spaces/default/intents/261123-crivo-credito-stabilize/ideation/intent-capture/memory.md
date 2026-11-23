# Ideation Intent Capture — Memory (SKIPPED — Brownfield)

> **Stage**: intent-capture | **Phase**: ideation | **Intent**: 261123-crivo-credito-stabilize
> **Date**: 2026-11-23 | **Agent**: Polaris (PM)
> **Status**: SKIPPED — Projeto brownfield com escopo definido

---

## Intent Statement
> Integrar AI-DLC ao Crivo Crédito Demo (brownfield) para governança, continuidade e stage gates com aprovação humana. Não é novo produto — é adoção de governança em projeto existente.

## Stakeholders
| Stakeholder | Papel | Interesse |
|-------------|-------|-----------|
| Rodrigo | PM / Product Owner | Governança, stage gates, continuidade, compliance |
| Equipe técnica | Tech Lead, Devs | Recuperação contexto, ADRs, CI/CD, qualidade |
| QA | QA Lead | Validação, testes, quality gates |

## Problem Statement
> Projeto brownfield funcional mas sem governança AI-DLC: sem handoff, sem ADRs, sem stage gates, sem memória persistente, sem integração Agentic-Home. Risco de perda de contexto, decisões irreversíveis sem aprovação, não auditável.

## Hipóteses de Valor
| Hipótese | Métrica de Sucesso |
|----------|-------------------|
| AI-DLC permite recuperação de contexto 100% entre sessões | Validate workflow: recuperação 100% funcional |
| Stage gates impedem decisões irreversíveis sem aprovação | Validate workflow: gates bloqueiam corretamente |
| Integração Agentic-Home reutiliza skills/templates | Skills carregáveis, templates referenciam Home |

## Escopo (In/Out)

### In Scope
- [x] Baseline de decisões históricas (ADRs 001-007)
- [x] Estrutura AI-DLC workspace (aidlc/)
- [x] Stage gates com aprovação humana (Gates 0-4)
- [x] Integração Agentic-Home (skills, templates, catálogo)
- [x] Handoff.md estendido com campos AI-DLC
- [x] Validação: recuperação, idempotência, rollback

### Out of Scope
- [ ] Novos features de negócio (motor de crédito, UI, etc.)
- [ ] Refatoração de código existente (preservar 100%)
- [ ] CI/CD implementation (fase Inception → delivery-planning)
- [ ] Testes padronizados pytest (fase Inception)
- [ ] Multi-tenancy, auth, produção (fora escopo POC)

## Riscos Identificados
| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Binários/segredos no repo | Alta | Médio | Documentado baseline; .gitignore ignora futuros |
| Conflito AGENTS.md vs AI-DLC state | Média | Médio | AGENTS.md aponta para aidlc/ como source of truth |
| Stage gates não respeitados | Baixa | Alto | Validate workflow testa bloqueio automático |
| Perda contexto entre sessões | Baixa | Alto | handoff.md + aidlc-state.md sincronizados |

## Critérios de Sucesso (Inception Complete)
- [x] Baseline documentado (ADRs 001-012)
- [x] ADRs baseline registradas (Implemented)
- [ ] Requirements analysis completa
- [ ] Domain design formalizado
- [ ] Contract design definido
- [ ] Delivery planning com pipeline, environments, quality gates
- [ ] Stage gate approval-handoff pronto para aprovação

## Próximos Passos
1. Aguardar Gate 2 (Baseline → Integrate) — Rodrigo (PM)
2. Executar Integrate workflow
3. Gate 3 (Integrate → Validate)
4. Executar Validate workflow
5. Gate 4 (Validate → Inception)
6. Iniciar Inception: requirements-analysis

---

*Ideation SKIPPED para brownfield — escopo já definido. Baseline registrado como ADRs 001-012.*