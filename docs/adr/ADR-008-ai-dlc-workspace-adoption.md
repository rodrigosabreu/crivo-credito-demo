# ADR-008: Adoção do AI-DLC workspace no projeto

## Status
Proposed

## Contexto
O projeto Crivo Crédito Demo é um brownfield funcional sem governança AI-DLC. Para garantir continuidade entre sessões, rastreabilidade de decisões, stage gates com aprovação humana e integração com o ecossistema Agentic-Home, é necessária a adoção do workspace AI-DLC.

## Decisão
Adotar estrutura AI-DLC completa em `aidlc/`:
- `aidlc/spaces/default/intents/<intent-id>/` — workspace por intent
- `aidlc-state.md` — estado operacional (fase, stage, next action)
- `project-description.json` — descrição canônica do projeto
- `project.md` — memória persistente (decisões, ADRs, contexto, riscos)
- `intents.json` — índice de intents
- Stage memories (`memory.md`) por fase/stage
- `approval-handoff/memory.md` — gates de aprovação humana
- `audit/` — trilha de auditoria

## Alternativas Consideradas
| Alternativa | Prós | Contras | Decisão |
|-------------|------|---------|---------|
| 1. Manter estado apenas no AGENTS.md | Simples, já existe | Sem estrutura, sem gates, sem recuperação confiável | Rejeitada |
| 2. AI-DLC parcial (apenas handoff + ADRs) | Menos arquivos | Incompleto, gaps de governança | Rejeitada |
| 3. AI-DLC completo conforme padrão | Padronizado, recuperável, gates, integração Home | Mais arquivos, curva de aprendizado | **Proposta** |

## Consequências
### Positivas
- Recuperação de contexto 100% funcional entre sessões
- Stage gates com aprovação humana obrigatória
- Integração nativa com Agentic-Home (skills, templates, catálogo)
- Auditoria completa de decisões e execução
- Idempotência e rollback testáveis

### Negativas
- Overhead inicial de setup
- Manutenção de arquivos de governança
- Curva de aprendizado para novos agentes

### Riscos
- Conflito AGENTS.md vs AI-DLC state (duas sources of truth)
- Templates ADR/handoff divergentes do Home
- Stage gates não respeitados sem validação automática

### Mitigações
- AGENTS.md aponta para `aidlc/` como source of truth operacional
- Estender templates Home, não copiar
- Validate workflow testa bloqueio automático de gates

## Impacto de Compliance
- [ ] Regulatório financeiro
- [ ] LGPD
- [ ] SOX
- [ ] PCI-DSS
- [ ] ANBIMA
- [ ] CMN 4.658
- [x] Outro: Governança AI-DLC para projetos do ecossistema

## Impacto AI-DLC
- **Eval gates afetados**: Gate 2 (Baseline → Integrate), Gate 3 (Integrate → Validate)
- **Pipeline changes**: Criação estrutura `aidlc/`, stage memories, gates
- **Observabilidade needs**: `aidlc-state.md` como health check
- **Model routing changes**: N/A
- **Cost impact**: Zero (arquivos markdown/JSON)

## Implementation Notes
- Estrutura criada no Workflow 4: Integrate
- Referenciar templates: `agentic-home/templates/handoff.md`, `agentic-home/templates/adr.md`
- Skills: `onboard-ai-dlc`, `descoberta`, `arquitetura`, `desenvolvimento`, `qualidade`

## References
- `agentic-home/skills/onboard-ai-dlc/` — skill de integração
- `agentic-home/templates/handoff.md` — template base
- `agentic-home/templates/adr.md` — template base
- `integration-plan.md` — plano detalhado

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