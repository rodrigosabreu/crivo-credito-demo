# ADR-005: Human-in-the-loop obrigatório (estado final `revisao_humana: pendente`)

## Status
Implemented

## Contexto
Nenhuma decisão de crédito automatizada pode ser final sem revisão humana. O sistema deve garantir que toda execução termine em estado que exija ação humana explícita.

## Decisão
- Estado final de toda execução: `revisao_humana: pendente`
- Transição obrigatória: `regras_executadas` → `analista` → `revisor` → `revisao_humana_necessaria`
- **Nenhum estado final automático** — sempre requer ação humana
- UI expõe botão "Revisão Humana" que marca como concluída (fora do escopo do motor)
- Concordância do revisor ≠ aprovação final — apenas acompanhamento

## Alternativas Consideradas
| Alternativa | Prós | Contras | Decisão |
|-------------|------|---------|---------|
| 1. Auto-aprovação se analista + revisor concordam | Rápido, automatizado | Viola princípio HITL, risco regulatório | Rejeitada |
| 2. Aprovação humana opcional (config) | Flexível | Inconsistente, pode ser desabilitado | Rejeitada |
| 3. HITL obrigatório hardcoded | Garantido, auditável, seguro | Requer ação manual sempre | **Aceita** |

## Consequências
### Positivas
- Conformidade regulatória: decisão humana documentada
- Segurança: evita decisões automatizadas não supervisionadas
- Auditoria: trilha mostra onde humano interveio
- Princípio: "Concordância ≠ correção" — revisor apenas acompanha

### Negativas
- Throughput limitado por disponibilidade humana
- Não adequado para alto volume automatizado

### Riscos
- Gargalo humano em escala
- Fadiga de revisão (rubber-stamping)

### Mitigações
- POC/sintética apenas — não para produção real
- Documentar: "Não validada juridicamente — não usar com dados reais"

## Impacto de Compliance
- [x] Regulatório financeiro (CVM, Bacen, etc.) — HITL obrigatório
- [ ] LGPD (Lei 13.709)
- [ ] SOX (Lei 11.941/2009)
- [ ] PCI-DSS
- [ ] ANBIMA
- [ ] CMN 4.658

## Impacto AI-DLC
- **Eval gates afetados**: Nenhum (decisão pré-existente)
- **Pipeline changes**: N/A
- **Observabilidade needs**: Estado `revisao_humana` rastreado em eventos
- **Model routing changes**: N/A
- **Cost impact**: Zero (POC)

## Implementation Notes
- `service.py`: `Service.executar()` → retorna `{"status": "revisao_humana", "revisao_humana": "pendente"}`
- `server.py`: Endpoint `GET /api/execucoes/{id}` expõe status
- UI: `index.html` mostra botão "Marcar Revisão Concluída" (simulado)

## References
- `crivo/service.py` — fluxo de execução e estado final
- `crivo/server.py` — endpoint de status
- `crivo/index.html` — UI de revisão

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