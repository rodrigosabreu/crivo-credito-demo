# ADR-003: Motor determinístico versionado `politica: demonstrativa-1.0`

## Status
Implemented

## Contexto
O motor de regras de crédito deve ser determinístico, versionado e imutável — agentes (simulados ou LLM via Hermes) não devem alterar as regras, apenas interpretá-las/aplicá-las.

## Decisão
- Policy versionada: `politica: demonstrativa-1.0` (string fixa no código)
- 3 regras fixas implementadas em `engine.py`:
  1. `regra_valor_minimo`: valor ≥ 1000
  2. `regra_parcelas_validas`: parcelas entre 1 e 60
  3. `regra_renda_compatível`: valor ≤ renda × 12
- Regras **não alteráveis por agentes** — apenas executadas
- Versionamento semântico da policy (major.minor) para mudanças deliberadas

## Alternativas Consideradas
| Alternativa | Prós | Contras | Decisão |
|-------------|------|---------|---------|
| 1. Regras em config/YAML externo | Flexível, não requer deploy | Agentes poderiam modificar, menos auditável | Rejeitada |
| 2. Regras hardcoded sem versionamento | Simples | Sem rastreabilidade de mudanças | Rejeitada |
| 3. Policy versionada hardcoded | Imutável, auditável, determinístico | Mudança requer code change | **Aceita** |

## Consequências
### Positivas
- Determinismo total: mesma entrada → mesma saída sempre
- Auditoria completa: policy version registrada em cada execução
- Segurança: agentes não podem alterar lógica de crédito
- Conformidade: trilha imutável para reguladores

### Negativas
- Mudança de regra = novo deploy + nova versão policy
- Menos flexível para experimentação rápida

### Riscos
- Policy version desatualizada vs regulamentação vigente

### Mitigações
- Processo de release para atualizações de policy
- Testes de regressão para cada versão

## Impacto de Compliance
- [x] Regulatório financeiro (CVM, Bacen, etc.) — Regras versionadas e auditáveis
- [ ] LGPD (Lei 13.709)
- [ ] SOX (Lei 11.941/2009)
- [ ] PCI-DSS
- [ ] ANBIMA
- [ ] CMN 4.658

## Impacto AI-DLC
- **Eval gates afetados**: Nenhum (decisão pré-existente)
- **Pipeline changes**: N/A
- **Observabilidade needs**: Policy version em cada execução (evento)
- **Model routing changes**: N/A
- **Cost impact**: Zero

## Implementation Notes
- `engine.py`: `POLITICA_VERSION = "demonstrativa-1.0"`
- `engine.executar_regras()`: retorna dict com `politica_version`, `regras_executadas`, `resultado`
- Event Sourcing registra `regras_executadas` + `politica_version` na tabela `events`

## References
- `crivo/engine.py` — linhas com POLITICA_VERSION e executar_regras()

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