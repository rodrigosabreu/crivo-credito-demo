# ADR-009: Stage gates com aprovação humana obrigatória

## Status
Proposed

## Contexto
O AI-DLC define stage gates obrigatórios entre fases para garantir que decisões irreversíveis tenham aprovação humana explícita. Para o Crivo Crédito Demo, os gates devem ser configurados com aprovadores definidos e critérios claros.

## Decisão
Implementar 5 gates obrigatórios baseados em `agentic-home/docs/governanca.md`:

| Gate | Transição | Aprovador | Critérios de Aprovação |
|------|-----------|-----------|------------------------|
| Gate 0 | Diagnose → Plan | Rodrigo (PM) | Diagnose report aprovado, classificação confirmada, gaps/risks validados |
| Gate 1 | Plan → Baseline | Rodrigo (PM) | Integration plan aprovado, stage gates definidos, rollback testável |
| Gate 2 | Baseline → Integrate | Rodrigo (PM) | Baseline commit capturado, ADRs históricos `Implemented`, gaps documentados |
| Gate 3 | Integrate → Validate | Rodrigo (PM) | Estrutura `aidlc/` completa, arquivos principais criados, AGENTS.md atualizado, handoff criado |
| Gate 4 | Validate → Inception | Rodrigo (PM) | Validation report APROVADO: recuperação 100%, idempotência, rollback, gates funcionais |

Cada gate:
- Bloqueia avanço automático sem aprovação registrada
- Registra aprovação/rejeição em `approval-handoff/memory.md`
- Template de aprovação com assinatura (role, name, date, signature)
- Rejeição volta stage anterior com `[R]` Revising

## Alternativas Consideradas
| Alternativa | Prós | Contras | Decisão |
|-------------|------|---------|---------|
| 1. Sem gates (avanço livre) | Rápido | Sem controle, decisões irreversíveis sem aprovação | Rejeitada |
| 2. Gates apenas entre fases maiores | Menos burocracia | Gap entre Inception→Construction crítico | Rejeitada |
| 3. 5 gates granulares com aprovador único | Controle total, rastreável | Mais overhead de aprovação | **Proposta** |

## Consequências
### Positivas
- Governança explícita: nenhuma fase avança sem aprovação
- Rastreabilidade: cada gate registra decisão, aprovador, data
- Bloqueio automático: validação em Validate workflow
- Alinhado com Agentic-Home governance

### Negativas
- Overhead: aguardar aprovação humana em cada gate
- Gargalo se aprovador indisponível

### Riscos
- Aprovador único (Rodrigo) = single point of failure
- Gates podem ser contornados manualmente

### Mitigações
- Documentar deputies/backup para aprovador
- Validate workflow testa bloqueio automático
- `aidlc-state.md` mostra gate status visível

## Impacto de Compliance
- [ ] Regulatório financeiro
- [ ] LGPD
- [ ] SOX
- [ ] PCI-DSS
- [ ] ANBIMA
- [ ] CMN 4.658
- [x] Outro: Governança de aprovação humana para AI-DLC

## Impacto AI-DLC
- **Eval gates afetados**: Todos os gates 0-4
- **Pipeline changes**: Criação `approval-handoff/memory.md` por gate
- **Observabilidade needs**: Gate status em `aidlc-state.md` e `handoff.md`
- **Model routing changes**: N/A
- **Cost impact**: Zero

## Implementation Notes
- `approval-handoff/memory.md` template em `references/approval-handoff-template.md`
- Gates criados no Integrate workflow
- Validação automática no Validate workflow
- Aprovador: Rodrigo (PM) — conforme governança Agentic-Home

## References
- `agentic-home/docs/governanca.md` — matriz de permissões e fluxos
- `integration-plan.md` — seção 3 Stage Gates
- `agentic-home/templates/handoff.md` — template base

## History
| Date | Version | Author | Change |
|------|---------|--------|--------|
| 2026-11-23 | 1.0 | Polaris (PM) | Initial proposal |

## Approval
| Role | Name | Date | Signature |
|------|------|------|-----------|
| Author | Polaris (PM) | 2026-11-23 | |
| Reviewer | | | |
| Approver | Rodrigo (PM) | | |
> **Gate**: Gate 2 (Baseline → Integrate) — Requer aprovação Rodrigo (PM)