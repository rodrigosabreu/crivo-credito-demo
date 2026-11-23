# ADR-011: Handoff.md estendido com campos AI-DLC

## Status
Proposed

## Contexto
O template padrão `agentic-home/templates/handoff.md` não inclui campos específicos do AI-DLC (fase, stage, gate status, phase gate status, intent ID). Para suportar recuperação de contexto e stage gates, o handoff do projeto deve ser estendido.

## Decisão
Estender `agentic-home/templates/handoff.md` com campos AI-DLC obrigatórios:

### Campos Adicionados
- **Phase**: Fase atual do AI-DLC (INITIALIZATION, IDEATION, INCEPTION, CONSTRUCTION, OPERATION)
- **Stage**: Stage atual (ex: reverse-engineering, requirements-analysis)
- **Gate Status**: Status do gate atual (OPEN, APPROVED, REJECTED, PENDING)
- **Phase Gate Status**: Status do gate de fase (ex: Gate 2: Baseline → Integrate)
- **Intent ID**: ID do intent ativo (ex: 261123-crivo-credito-stabilize)
- **AI-DLC State Source**: Caminho para `aidlc-state.md` (source of truth operacional)
- **Next Action**: Próxima ação executável (do `aidlc-state.md` Session Resume Point)
- **Blocking Gates**: Lista de gates bloqueando avanço

### Estrutura do Handoff Estendido
```markdown
# Task Handoff — Crivo Crédito Demo

## AI-DLC Context
- **Phase**: INCEPTION
- **Stage**: reverse-engineering (baseline registration)
- **Gate Status**: PENDING (Gate 2: Baseline → Integrate)
- **Phase Gate Status**: Gate 2 awaiting approval
- **Intent ID**: 261123-crivo-credito-stabilize
- **AI-DLC State Source**: aidlc/spaces/default/intents/261123-crivo-credito-stabilize/aidlc-state.md
- **Next Action**: Aguardar aprovação Gate 2 por Rodrigo (PM), então executar Integrate workflow
- **Blocking Gates**: Gate 2 (Baseline → Integrate)

## Task Info
...
```

### Sincronização
- `handoff.md` ↔ `aidlc-state.md` devem ser consistentes
- Atualização em cada transição de stage/gate
- Validate workflow verifica consistência

## Alternativas Consideradas
| Alternativa | Prós | Contras | Decisão |
|-------------|------|---------|---------|
| 1. Usar template Home sem extensão | Simples, padrão | Perde contexto AI-DLC, gates não visíveis | Rejeitada |
| 2. Handoff separado AI-DLC | Isolado | Duplicação, divergência | Rejeitada |
| 3. Estender template Home (escolhida) | Único source, campos AI-DLC visíveis, padronizado | Template Home muda → revisar extensão | **Proposta** |

## Consequências
### Positivas
- Recuperação de contexto completa em uma leitura
- Gates visíveis no handoff (não só no aidlc-state.md)
- Padronização com Home mantida (extensão, não cópia)
- Agentes novos recuperam fase/stage/gate/next-action imediatamente

### Negativas
- Template Home muda → extensão precisa revisão
- Mais campos para manter sincronizados

### Riscos
- Divergência handoff.md vs aidlc-state.md
- Campos AI-DLC não preenchidos/atualizados

### Mitigações
- Validate workflow testa consistência handoff ↔ aidlc-state
- Convenção: atualizar ambos em cada transição
- `aidlc-state.md` é source of truth operacional; handoff.md é resumo para handoff

## Impacto de Compliance
- [ ] Regulatório financeiro
- [ ] LGPD
- [ ] SOX
- [ ] PCI-DSS
- [ ] ANBIMA
- [ ] CMN 4.658
- [x] Outro: Continuidade operacional AI-DLC

## Impacto AI-DLC
- **Eval gates afetados**: Gate 3 (Integrate → Validate) valida handoff criado
- **Pipeline changes**: handoff.md criado/atualizado no Integrate workflow
- **Observabilidade needs**: Handoff como health check de continuidade
- **Model routing changes**: N/A
- **Cost impact**: Zero

## Implementation Notes
- Template base: `agentic-home/templates/handoff.md`
- Extensão definida em `references/approval-handoff-template.md` (skill onboard-ai-dlc)
- Criado no Integrate workflow
- Atualizado em cada stage/gate transition

## References
- `agentic-home/templates/handoff.md` — template base
- `onboard-ai-dlc/references/approval-handoff-template.md` — campos AI-DLC
- `integration-plan.md` — seção 8.2 (ADR-011)
- `aidlc-state.md` — source of truth operacional

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