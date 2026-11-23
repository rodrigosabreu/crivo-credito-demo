# ADR-004: Event Sourcing para auditoria (tabela `events`)

## Status
Implemented

## Contexto
Toda decisão de crédito deve ter trilha de auditoria imutável e rastreável. A aplicação precisa registrar cada etapa: cenário selecionado → regras executadas → analista → revisor → revisão humana necessária.

## Decisão
- Event Sourcing implementado via tabela `events` no SQLite
- Cada execução (`runs` table) gera sequência de eventos imutáveis
- Eventos: `cenario_selecionado` → `regras_executadas` → `analista` → `revisor` → `revisao_humana_necessaria`
- Eventos **nunca modificados/eliminados** — append-only
- `run_id` correlação entre `runs` e `events`
- Payload JSON com detalhes completos de cada etapa

## Alternativas Consideradas
| Alternativa | Prós | Contras | Decisão |
|-------------|------|---------|---------|
| 1. Logs em arquivo/texto | Simples | Não estruturado, difícil query | Rejeitada |
| 2. Apenas tabela `runs` com status final | Simples | Perde histórico intermediário | Rejeitada |
| 3. Event Sourcing (tabela events) | Trilha completa, imutável, queryável | Mais storage, complexidade | **Aceita** |

## Consequências
### Positivas
- Auditoria completa: cada passo rastreável
- Debugging: reproduzir execução exata via eventos
- Compliance: atende requisitos de rastreabilidade
- Base para analytics futuros

### Negativas
- Storage cresce linearmente com execuções
- Mais complexidade no Service

### Riscos
- PII em eventos (dados do cenário) — mas dados são sintéticos

### Mitigações
- Dados sintéticos apenas — zero PII real
- Retenção: documentar política (ex: 1 ano)

## Impacto de Compliance
- [x] Regulatório financeiro (CVM, Bacen, etc.) — Trilha auditoria completa
- [ ] LGPD (Lei 13.709) — Dados sintéticos, mas princípio aplicável
- [ ] SOX (Lei 11.941/2009)
- [ ] PCI-DSS
- [ ] ANBIMA
- [ ] CMN 4.658

## Impacto AI-DLC
- **Eval gates afetados**: Nenhum (decisão pré-existente)
- **Pipeline changes**: N/A
- **Observabilidade needs**: Eventos disponíveis para métricas
- **Model routing changes**: N/A
- **Cost impact**: Mínimo (SQLite local)

## Implementation Notes
- `service.py`: `Service.persistir_evento()` — insert na tabela `events`
- Schema: `events(id, run_id, etapa, payload_json, timestamp)`
- Etapas: `cenario_selecionado`, `regras_executadas`, `analista`, `revisor`, `revisao_humana_necessaria`
- Endpoint: `GET /api/execucoes/{id}/eventos` retorna trilha completa

## References
- `crivo/service.py` — `persistir_evento()`, `obter_eventos()`
- `crivo/engine.py` — retorna `regras_executadas` para evento

## History
| Date | Version | Author | Change |
|------|---------|--------|--------|
| 2026-11-21 | 1.0 | (original) | Initial implementation |
| 2026-11-23 | 1.1 | Polaris (PM) | Registered as baseline historical decision |

## Approval
| Role | Name | Date | Signature |
|------|------|------|-----------|
| Author | (original developer) | 2026-11-21 | |
| Reviewer | | | |
| Approver | | | |
> **Nota**: Decisão implementada em 2026-11-21 (commit f7748c6), registrada como baseline histórico **sem aprovação retroativa** conforme política AI-DLC.