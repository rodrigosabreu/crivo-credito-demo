# ADR-012: Baseline de decisões históricas como ADRs `Implemented`

## Status
Proposed

## Contexto
Projetos brownfield possuem decisões arquiteturais já implementadas no código/histórico. O AI-DLC exige que essas decisões sejam registradas como ADRs para rastreabilidade, mas **sem inventar aprovações retroativas** — devem ser marcadas como baseline histórico.

## Decisão
Para decisões já implementadas no código (brownfield):
1. Criar ADRs com status `Implemented` (não `Accepted`/`Proposed`)
2. **Não atribuir aprovação retroativa** — campos Author/Reviewer/Approver preenchidos com "(original developer)" e data do commit original
3. Header do ADR incluir nota: "Decisão implementada em [data/commit], registrada como baseline histórico sem aprovação retroativa"
4. Section `Approval` incluir nota: "> **Nota**: Decisão implementada em [data] (commit [hash]), registrada como baseline histórico **sem aprovação retroativa** conforme política AI-DLC."
5. Documentar fonte: arquivo/linha do código onde decisão é evidenciada
6. Gaps e não-decisões registrados como pendências (não criam ADRs)

### ADRs Baseline para Crivo Crédito Demo (7 ADRs)
| ADR | Título | Commit | Fonte |
|-----|--------|--------|-------|
| ADR-001 | Stack Python 3.10+ stdlib + SQLite | f7748c6 | engine.py, service.py, server.py |
| ADR-002 | Arquitetura 4 camadas + DI | f7748c6 | engine.py, service.py, hermes.py |
| ADR-003 | Motor determinístico versionado | f7748c6 | engine.py |
| ADR-004 | Event Sourcing (tabela events) | f7748c6 | service.py |
| ADR-005 | Human-in-the-loop obrigatório | f7748c6 | service.py |
| ADR-006 | Security-first: loopback + origin + CSRF | f7748c6 | server.py, demo.py |
| ADR-007 | Dois modos: simulado/hermes opt-in | f7748c6 | service.py, hermes.py, server.py |

### Gaps Documentados (Não-ADRs)
- CI/CD ausente → Pendência para delivery-planning
- Testes sem framework padrão → Pendência para requirements-analysis
- Sem gestão dependências → Pendência para delivery-planning
- Sem code quality tools → Pendência para delivery-planning
- Binários/segredos no repo → Documentado no baseline, não removido do histórico

## Alternativas Consideradas
| Alternativa | Prós | Contras | Decisão |
|-------------|------|---------|---------|
| 1. Não criar ADRs para decisões passadas | Simples | Perde rastreabilidade, auditoria incompleta | Rejeitada |
| 2. Criar ADRs `Accepted` com aprovação atual | Formal | Finge aprovação que não aconteceu, antiético | Rejeitada |
| 3. Criar ADRs `Implemented` sem aprovação retroativa (escolhida) | Honesto, rastreável, baseline claro | Requer disciplina para não inventar aprovações | **Proposta** |

## Consequências
### Positivas
- Honestidade: não finge aprovações que não ocorreram
- Rastreabilidade: decisões passadas documentadas e auditáveis
- Baseline claro: ponto de partida conhecido para governança futura
- Gaps explícitos: o que falta é visível e priorizável

### Negativas
- ADRs `Implemented` não têm aprovação formal (por design)
- Pode confundir com ADRs `Accepted` se não bem documentado

### Riscos
- Auditor pode questionar falta de aprovação em ADRs `Implemented`
- Tentação de preencher campos Approver retroativamente

### Mitigações
- Nota explícita em cada ADR baseline: "sem aprovação retroativa"
- Política AI-DLC documentada: baseline ≠ aprovação
- Validate workflow verifica: nenhum ADR baseline com aprovação inventada

## Impacto de Compliance
- [ ] Regulatório financeiro
- [ ] LGPD
- [ ] SOX
- [ ] PCI-DSS
- [ ] ANBIMA
- [ ] CMN 4.658
- [x] Outro: Integridade de auditoria — baseline honesto

## Impacto AI-DLC
- **Eval gates afetados**: Gate 2 (Baseline → Integrate) valida ADRs baseline criados
- **Pipeline changes**: 7 ADRs criados no Baseline workflow
- **Observabilidade needs**: Contagem ADRs baseline vs propostos
- **Model routing changes**: N/A
- **Cost impact**: Zero

## Implementation Notes
- Criados no Baseline workflow (Workflow 3 da skill onboard-ai-dlc)
- Localização: `docs/adr/ADR-XXX-*.md`
- Template: `agentic-home/templates/adr.md` estendido
- Registrados em `aidlc-state.md` Baseline Artifacts
- Registrados em `project.md` tabela Decisões Arquiteturais

## References
- `agentic-home/templates/adr.md` — template base
- `integration-plan.md` — seção 8.1 (ADRs Baseline)
- `diagnose-report.md` — seção 3 (Arquitetura identificada)
- `onboard-ai-dlc` skill — Workflow 3: Baseline

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