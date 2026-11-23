# Project Memory — Crivo Crédito Demo

> **Intent**: 261123-crivo-credito-stabilize | **Phase**: INCEPTION | **Stage**: approval-handoff (AGUARDANDO GATE 5)
> **Baseline Commit**: 82c9900 | **Baseline Date**: 2026-11-23
> **Source of Truth**: aidlc-state.md (estado operacional), este arquivo (memória decisões/contexto)

---

## Decisões Arquiteturais (ADRs)

### Baseline (Implementadas — status `Implemented`)
Decisões extraídas do código/histórico, registradas como baseline histórico **sem aprovação retroativa**.

| ADR | Título | Status | Resumo | Fonte |
|-----|--------|--------|--------|-------|
| ADR-001 | Stack Python 3.10+ stdlib + SQLite | Implemented | Zero deps, SQLite embarcado, http.server nativo | engine.py, service.py, server.py |
| ADR-002 | Arquitetura 4 camadas + DI | Implemented | Engine → Service → Server → Adapters injetáveis | engine.py, service.py, hermes.py |
| ADR-003 | Motor determinístico versionado | Implemented | politica: demonstrativa-1.0, 3 regras fixas, imutável | engine.py |
| ADR-004 | Event Sourcing (tabela events) | Implemented | Trilha imutável: cenario → regras → analista → revisor → revisao_humana | service.py |
| ADR-005 | Human-in-the-loop obrigatório | Implemented | Estado final sempre revisao_humana: pendente | service.py |
| ADR-006 | Security-first: loopback + origin + CSRF | Implemented | Bind 127.0.0.1:8000, validação Origin/Referer, CSRF demo | server.py, demo.py |
| ADR-007 | Dois modos: simulado (default) / hermes (opt-in) | Implemented | DI via CRIVO_MODO, sem fallback automático | service.py, hermes.py, server.py |

### Governança AI-DLC (Propostas — status `Proposed`)
Decisões de governança para integração AI-DLC, pendentes aprovação via stage gates.

| ADR | Título | Status | Resumo | Gate |
|-----|--------|--------|--------|------|
| ADR-008 | Adoção AI-DLC workspace | Proposed | Estrutura aidlc/, stage gates, handoff, memória persistente | Gate 2 |
| ADR-009 | Stage gates aprovação humana | Proposed | Gates 0-4 obrigatórios, aprovador Rodrigo (PM), bloqueio automático | Gate 2 |
| ADR-010 | Integração Agentic-Home | Proposed | Skills descoberta/arquitetura/desenvolvimento/qualidade, templates, catálogo | Gate 2 |
| ADR-011 | Handoff.md estendido AI-DLC | Proposed | Campos: phase, stage, gate_status, phase_gate_status, intent_id | Gate 2 |
| ADR-012 | Baseline histórico como Implemented | Proposed | ADRs 001-007 Implemented sem aprovação retroativa, gaps documentados | Gate 2 |

---

## Gaps e Pendências (Não-ADRs)

Identificados no Diagnose, documentados no Integration Plan, endereçados nas fases futuras:

| Gap | Fase Alvo | Status |
|-----|-----------|--------|
| CI/CD ausente | Inception → delivery-planning | **Endereçado no Delivery Planning (Sprint 1)** |
| Testes customizados sem framework padrão (pytest) | Inception → requirements-analysis | **Endereçado no Delivery Planning (Sprint 1)** |
| Sem gestão dependências (requirements.txt/pyproject.toml) | Inception → delivery-planning | **Endereçado no Delivery Planning (Sprint 1)** |
| Sem code quality (linter, formatter, type checker) | Inception → delivery-planning | **Endereçado no Delivery Planning (Sprint 1)** |
| Binários/segredos no repo (cloudflared 40MB, password) | Baseline (documentado) | **Documentado — não removido do histórico** |
| Handoff.md, ADRs, stage gates ausentes | Baseline + Integrate | **Concluído (Integrate + Inception)** |

---

## Riscos Identificados (do Diagnose/Plan)

| Risco | Prob | Impacto | Mitigação |
|-------|------|---------|-----------|
| Binários/segredos no repo | Alta | Médio | Documentado no baseline; .gitignore ignora futuros |
| Ausência CI/CD | Alta | Médio | delivery-planning definirá pipeline (Sprint 1) |
| Testes dependem infra externa (cloudflared) | Média | Médio | Modo simulado padrão; testes Hermes = integration tests separados |
| Conflito AGENTS.md vs AI-DLC state | Média | Médio | AGENTS.md aponta para aidlc/ como source of truth operacional |
| Stage gates não respeitados | Baixa | Alto | Validate workflow testa bloqueio automático |
| Perda contexto entre sessões | Baixa | Alto | handoff.md + aidlc-state.md sincronizados; teste recuperação em Validate |
| Rollback integração AI-DLC | Baixa | Crítico | Tags Git pre/post cada fase; rollback testado em Validate |

---

## Contexto Operacional

### Modos de Execução
- **Simulado (padrão)**: `python run_server.py` → roda imediato, zero config
- **Hermes (opt-in)**: `CRIVO_MODO=hermes` + gateway rodando + chaves → analista/revisor via LLM

### Cenários Sintéticos
| ID | Título | Descrição |
|----|--------|-----------|
| completo | Completo e consistente | Todos campos presentes, valores válidos |
| ausente | Dados ausentes | valor e total_declarado são null |
| divergente | Total divergente | total_declarado ≠ valor × parcelas |
| violacao | Parcelas inválidas | parcelas = 0 (divisão por zero) |

### API Endpoints
- `GET /api/cenarios` — Lista cenários
- `POST /api/execucoes` — Executa simulação `{ "cenario": "completo" }`
- `GET /api/execucoes/{id}` — Resultado + status
- `GET /api/execucoes/{id}/eventos` — Trilha de eventos (Event Sourcing)
- `GET /ui` — Interface web single-page

### Segurança (Regras Obrigatórias)
1. Zero dados reais — catálogo sintético fixo
2. Regras versionadas imutáveis — agentes não alteram motor
3. Concordância ≠ correção — revisor apenas acompanha
4. Human-in-the-loop obrigatório — estado final revisao_humana: pendente
5. Origem rastreada — adaptadores.analista/revisor = simulado_local ou adaptador_hermes_...
6. Sem fallback automático — falha → parecer falha + revisão humana
7. Não expor serviços — 127.0.0.1:8000 only
8. Sem auth/autorização — POC não endurecida
9. Não validada juridicamente — não usar com dados reais

---

## Integração Agentic-Home

- **Skills**: descoberta, arquitetura, desenvolvimento, qualidade, onboard-ai-dlc
- **Templates**: handoff.md, adr.md (estendidos com campos AI-DLC)
- **Catálogo**: projects/catalogo.md (entrada crivo-credito-demo registrada)
- **Governança**: docs/governanca.md (stage gates, matriz permissões)
- **Onboarding**: docs/onboarding.md

---

## Fases Inception Concluídas

| Stage | Status | Artefato Principal |
|-------|--------|-------------------|
| 1.1 reverse-engineering | ✅ CONCLUÍDA | `inception/reverse-engineering/memory.md` |
| 1.2 requirements-analysis | ✅ CONCLUÍDA | `inception/requirements-analysis/memory.md` (274 linhas) |
| 1.3 domain-design | ✅ CONCLUÍDA | `inception/domain-design/memory.md` |
| 1.4 contract-design | ✅ CONCLUÍDA | `inception/contract-design/memory.md` (1173 linhas) |
| 1.5 delivery-planning | ✅ CONCLUÍDA | `inception/delivery-planning/memory.md` (261 linhas) |
| 1.6 approval-handoff | 🟡 AGUARDANDO GATE 5 | `inception/approval-handoff/memory.md` |

---

## Próximas Ações

1. **Gate 5 Approval**: Aprovação Rodrigo (PM) + Tech Lead + QA — Inception → Construction
2. **Criar tag** `post-inception-delivery-planning` (aponta para commit atual)
3. **Iniciar Sprint 1 Construction** — `pyproject.toml` + test suite + CI/CD + OpenAPI endpoint
4. **Iniciar Construction**: functional-design (stage 2.1) → code-generation (stage 2.2) → build-and-test (stage 2.3) → ci-pipeline (stage 2.4) → quality-gates (stage 2.5)

---

## Referências

- **Inception Stages Memories**: `aidlc/spaces/default/intents/261123-crivo-credito-stabilize/inception/*/memory.md`
- **Handoff**: `handoff.md` (raiz do projeto)
- **AI-DLC State**: `aidlc/spaces/default/intents/261123-crivo-credito-stabilize/aidlc-state.md`
- **Audit Trail**: `aidlc/spaces/default/intents/261123-crivo-credito-stabilize/audit/trail.md`
- **ADRs**: `docs/adr/ADR-001` a `ADR-012`

---

*Memória persistente do projeto. Atualize quando houver novas decisões, ADRs aprovados, gaps resolvidos ou mudanças de fase/stage. Sincronize com aidlc-state.md.*