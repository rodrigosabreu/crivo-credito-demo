# Delivery Planning — Memory
> **Stage**: delivery-planning | **Phase**: inception | **Intent**: 261123-crivo-credito-stabilize
> **Date**: 2026-11-23 | **Agent**: Polaris (PM)

---

## Objetivo

Traduzir os outputs de **Requirements Analysis** (19 RFs, 20 RNFs, 36 ACs, 12 Gaps), **Domain Design** (modelo DDD, 14 regras de negócio, 8 perguntas abertas) e **Contract Design** (OpenAPI 3.0, Ports/Adapters, Event Schemas, Config Contracts, Hermes Integration) em um plano de entrega acionável para a fase **Construction**:

- Priorizar os 12 gaps identificados (GAP-001 a GAP-012)
- Definir sprints de Construction com escopo, critérios de aceite e estimativas
- Estabelecer **Definition of Done** (DoD) para o projeto
- Identificar dependências, riscos e decisões pendentes
- Preparar handoff para Gate 5 (Inception → Construction)

---

## Contexto de Entrada

| Artefato | Status | Principais Outputs |
|----------|--------|-------------------|
| Requirements Analysis | ✅ Concluído | 19 RFs, 20 RNFs, 10 cenários, 8 ambiguidades, 36 ACs, 12 Gaps, mapeamento código, tradeoffs |
| Domain Design | ✅ Concluído | Bounded Context único, Agregado ExecucaoSimulacao, 2 Entidades, 6 VOs, 5 Domain Events, 4 Domain Services, 14 Regras de Negócio (RN-001 a RN-014), análise anêmico vs rich, ACL Hermes, 8 perguntas abertas (DOM-001 a DOM-008) |
| Contract Design | ✅ Concluído | OpenAPI 3.0 (25 schemas, 6 endpoints), AnalystPort/ReviewerPort (Protocol), 3 adapters (Simulated ×2, Hermes ×2), 5 Event Schemas (JSON Schema), Config Contracts (env vars + feature flags + JSON Schema), Hermes Integration Contracts (envelope + 17 validações), 6 tradeoffs, 6 perguntas abertas (CON-001 a CON-006) |

---

## 1. Priorização de Gaps (GAP-001 a GAP-012)

### Matriz de Priorização (RICE adaptado)

| Gap ID | Descrição | Reach (usuários afetados) | Impact (valor/risco) | Confidence (certeza) | Effort (dias) | RICE Score | Prioridade | Sprint Alvo |
|--------|-----------|---------------------------|----------------------|----------------------|---------------|------------|------------|-------------|
| **GAP-001** | Sem testes automatizados (pytest); apenas scripts customizados | Alto (todo time, CI) | Alto (qualidade, regressão) | Alto | 3 | **Alto** | **P0 — Crítico** | Sprint 1 |
| **GAP-002** | Sem CI/CD pipeline | Alto (todo time, deploy) | Alto (automação, qualidade) | Alto | 2 | **Alto** | **P0 — Crítico** | Sprint 1 |
| **GAP-003** | Sem gestão de dependências (`pyproject.toml`) | Médio (DX, onboarding) | Médio (manutenibilidade) | Alto | 1 | **Médio** | **P1 — Alto** | Sprint 1 |
| **GAP-004** | Sem linter/formatter/type checker | Médio (DX, qualidade código) | Médio (consistência) | Alto | 1 | **Médio** | **P1 — Alto** | Sprint 1 |
| **GAP-005** | Binário `cloudflared` (40MB) + segredo `password` no repo | Baixo (já público) | Alto (segurança, compliance) | Alto | 0 (documentado) | **Baixo** | **P2 — Documentado** | N/A (baseline) |
| **GAP-006** | Revisor simulado nunca retorna `contesta` | Baixo (cobertura cenário) | Baixo (POC scope) | Médio | 0.5 | **Baixo** | **P3 — Opcional** | Sprint 3 (se aprovado) |
| **GAP-007** | Métricas performance (NFR-004, NFR-005) não validadas | Médio (capacidade) | Médio (planejamento) | Baixo | 1 | **Médio** | **P2 — Validar** | Sprint 2 |
| **GAP-008** | Sem health check / readiness probe | Baixo (ops) | Baixo (observabilidade) | Alto | 0.5 | **Baixo** | **P3 — Opcional** | Sprint 2 |
| **GAP-009** | Sem limite de conexões/threads no ThreadingHTTPServer | Baixo (escala) | Baixo (POC scope) | Médio | 0.5 | **Baixo** | **P3 — Opcional** | Sprint 3 |
| **GAP-010** | Event Sourcing não imutável criptograficamente | Baixo (auditoria atual) | Médio (compliance futuro) | Baixo | 2 | **Médio** | **P2 — Avaliar** | Sprint 3 (se compliance exigir) |
| **GAP-011** | Modo Hermes: sem circuit breaker, retry, observabilidade | Médio (resiliência Hermes) | Médio (confiabilidade opt-in) | Médio | 2 | **Médio** | **P1 — Alto** | Sprint 2 |
| **GAP-012** | Sem documentação de API (OpenAPI/Swagger) | Médio (DX, contrato) | Médio (contrato formal) | Alto | 1 (já especificado no Contract Design) | **Médio** | **P1 — Alto** | Sprint 1 |

### Resumo de Prioridades

| Prioridade | Gaps | Esforço Total (dias) | Sprint |
|------------|------|---------------------|--------|
| **P0 — Crítico** | GAP-001, GAP-002 | 5 | Sprint 1 |
| **P1 — Alto** | GAP-003, GAP-004, GAP-011, GAP-012 | 6 | Sprint 1-2 |
| **P2 — Médio** | GAP-007, GAP-008, GAP-010 | 3.5 | Sprint 2-3 |
| **P3 — Opcional** | GAP-006, GAP-009 | 1 | Sprint 3 |
| **Baseline (documentado)** | GAP-005 | 0 | N/A |

---

## 2. Planejamento de Sprints (Construction Phase)

### Sprint 1 — **Foundation & Quality Gates** (5 dias úteis)
**Objetivo**: Estabelecer infraestrutura de qualidade, testes e CI/CD — base para tudo o resto.

| Item | Descrição | Critérios de Aceite | Estimativa | Dono |
|------|-----------|---------------------|------------|------|
| **S1-01** | Criar `pyproject.toml` com: `pytest`, `ruff`, `mypy`, `black`, deps opcionais (`hermes` extra) | `pip install -e .` funciona; `pytest`, `ruff`, `mypy`, `black` executáveis | 1 dia | Dev |
| **S1-02** | Implementar test suite pytest cobrindo: engine (3 regras × 4 cenários), service (analista, revisor, falhas, orquestração), server (API endpoints, validação, origin), hermes (adapter validação) | ≥ 90% coverage em `crivo/`; todos ACs dos Requirements Analysis validados por testes | 2 dias | Dev + QA |
| **S1-03** | Configurar GitHub Actions CI: lint (ruff), type-check (mypy), format-check (black), test (pytest), security (bandit opcional) | Pipeline roda em PR + push main; falha em qualquer step bloqueia merge | 1 dia | Dev |
| **S1-04** | Publicar OpenAPI spec em `/api/openapi.yaml` (endpoint) + validar conformidade com Contract Design | `GET /api/openapi.yaml` retorna spec YAML válido; `redoc` ou `swagger-ui` opcional | 1 dia | Dev |

**Entregável Sprint 1**: Projeto com testes automatizados, CI/CD funcional, gestão de deps, documentação de API publicada.

---

### Sprint 2 — **Resilience & Observability** (4 dias úteis)
**Objetivo**: Endereçar gaps de resiliência (Hermes), observabilidade e validar performance.

| Item | Descrição | Critérios de Aceite | Estimativa | Dono |
|------|-----------|---------------------|------------|------|
| **S2-01** | Implementar Circuit Breaker + Retry + Timeout configurável no `HermesAdapter` | Adapter falha rápido após N erros; retry com backoff; métricas de latência/erro expostas | 2 dias | Dev |
| **S2-02** | Adicionar endpoint `/health` (readiness + liveness) + health check SQLite | `GET /health` retorna `{status: "ok", checks: {db: true, hermes: true/false}}`; usado por probes | 0.5 dia | Dev |
| **S2-03** | Benchmark de performance: validar NFR-004 (<100ms p99) e NFR-005 (≥10 req/s) | Script de carga documenta resultados; targets confirmados ou ajustados | 1 dia | Dev + QA |
| **S2-04** | Implementar limitação de conexões/threads no ThreadingHTTPServer (pool) | `ThreadingHTTPServer` com `max_children` ou semáforo; teste de carga não OOM | 0.5 dia | Dev |

**Entregável Sprint 2**: Adapter Hermes resiliente, health checks, performance validada, server protegido contra exaustão.

---

### Sprint 3 — **Domain Evolution & Compliance** (5 dias úteis)
**Objetivo**: Evoluir modelo de domínio (Rich Model, ACL), endereçar compliance e gaps opcionais.

| Item | Descrição | Critérios de Aceite | Estimativa | Dono |
|------|-----------|---------------------|------------|------|
| **S3-01** | Implementar `ports.py` com `AnalystPort`, `ReviewerPort` (Protocol runtime_checkable) | Ports definidos; validação runtime em `service.run`; adapters existentes ajustados | 1 dia | Dev |
| **S3-02** | Implementar `adapters/simulated.py` (`SimulatedAnalystAdapter`, `SimulatedReviewerAdapter`) | Adapters implementam Ports; validação `_valid` movida para adapters; testes passam | 1 dia | Dev |
| **S3-03** | Implementar `adapters/hermes.py` (`HermesAnalystAdapter`, `HermesReviewerAdapter`) com ACL | Adapters implementam Ports; validação de contrato Hermes; isolamento de domínio; testes passam | 2 dias | Dev |
| **S3-04** | Refatorar `service.py` para usar Ports (DI) em vez de funções diretas | `service.run(analyst: AnalystPort, reviewer: ReviewerPort)`; zero breaking changes em API | 1 dia | Dev |

**Itens Condicionais (dependem de decisões PO/Tech Lead/Compliance):**

| Item | Condição | Descrição |
|------|----------|-----------|
| **S3-05** | Se DOM-008 aprovado (revisor `contesta`) | Ajustar `SimulatedReviewerAdapter` para retornar `contesta` em cenário específico |
| **S3-06** | Se AMB-003/Compliance exigir | Adicionar assinatura criptográfica/hashing aos eventos (GAP-010) |
| **S3-07** | Se DOM-002 aprovado (políticas configuráveis) | Extrair regras para configuração versionada (JSON/YAML/DB) |
| **S3-08** | Se DOM-004 aprovado (ACL explícito) | Itens S3-01 a S3-04 já cobrem; validar completude |

**Entregável Sprint 3**: Ports/Adapters implementados (ACL), domínio desacoplado de Hermes, base para evolução futura.

---

### Sprint 4 — **Hardening & Gate 5 Prep** (3 dias úteis)
**Objetivo**: Consolidação, testes de integração completos, preparação para aprovação Gate 5.

| Item | Descrição | Critérios de Aceite | Estimativa | Dono |
|------|-----------|---------------------|------------|------|
| **S4-01** | Testes de integração E2E: fluxo completo simulado + Hermes (mock) | Cenários `completo`, `ausente`, `divergente`, `violacao` validados E2E; Hermes mock testado | 1 dia | QA + Dev |
| **S4-02** | Validação de todos ACs (36) via testes automatizados | Relatório de coverage mapeia cada AC → teste(s); 100% ACs cobertos | 1 dia | QA |
| **S4-03** | Documentação final: README atualizado, ADRs de decisões Construction, runbook básico | `README.md` reflete stack final; ADRs para decisões tomadas (ex: Ports, Circuit Breaker); runbook operativo | 1 dia | PM + Dev |

**Entregável Sprint 4**: Sistema validado end-to-end, documentado, pronto para Gate 5 (Inception → Construction).

---

## 3. Definition of Done (DoD)

### DoD — Nível de Item (Story/Task)
Um item de backlog está **Done** quando:

- [ ] Código implementado seguindo padrões do projeto (Python stdlib, type hints, docstrings)
- [ ] Testes unitários + integração cobrindo funcionalidade (≥ 90% coverage em arquivos alterados)
- [ ] Testes passam localmente (`pytest -xvs`)
- [ ] Lint limpo (`ruff check .`), type-check limpo (`mypy crivo/`), format ok (`black --check .`)
- [ ] CI/CD pipeline passa (GitHub Actions: lint, type-check, test, security)
- [ ] Documentação atualizada (README, docstrings, OpenAPI se endpoint alterado)
- [ ] ACs relacionados validados e rastreáveis
- [ ] Code review aprovado por pelo menos 1 dev (ou Tech Lead)
- [ ] Merge em `main` via PR com checks passando

### DoD — Nível de Sprint
Uma sprint está **Done** quando:

- [ ] Todos itens do Sprint Backlog atendem DoD de item
- [ ] Sprint Review realizada com stakeholders (PO, Tech Lead, QA)
- [ ] Retrospectiva realizada; ações de melhoria registradas
- [ ] Incremento potencialmente entregável (deployável em staging/local)
- [ ] Métricas de sprint registradas (velocity, bugs escapados, lead time)

### DoD — Nível de Release (Gate 5 → Construction)
O projeto está pronto para **Construction** quando:

- [ ] **Todos P0 e P1 gaps endereçados** (GAP-001, 002, 003, 004, 011, 012)
- [ ] **Test suite completa** (≥ 90% coverage, 36 ACs validados)
- [ ] **CI/CD pipeline funcional** e rodando em `main`
- [ ] **Ports/Adapters implementados** (ACL Hermes) — S3-01 a S3-04
- [ ] **OpenAPI spec publicada** e validada
- [ ] **Health checks** implementados
- [ ] **Performance benchmarks** documentados (NFR-004, NFR-005)
- [ ] **Circuit Breaker + Retry** no HermesAdapter
- [ ] **ADRs de decisões Construction** registrados (mínimo: Ports, Circuit Breaker, Test Strategy)
- [ ] **Gate 5 aprovado** por Rodrigo (PM) + Tech Lead + QA

---

## 4. Estimativas de Esforço Consolidado

| Fase | Sprints | Dias Úteis | Esforço Total (pessoa-dias) |
|------|---------|------------|------------------------------|
| **Sprint 1** | Foundation & Quality Gates | 5 | 5 |
| **Sprint 2** | Resilience & Observability | 4 | 4 |
| **Sprint 3** | Domain Evolution & Compliance | 5 | 5 |
| **Sprint 4** | Hardening & Gate 5 Prep | 3 | 3 |
| **Total Construction** | 4 sprints | **17 dias úteis** | **17 pessoa-dias** |

> **Nota**: Estimativas assumem 1 dev full-time + QA part-time (0.5 FTE) + PM part-time (0.25 FTE). Ajustar conforme capacity real do time.

---

## 5. Dependências e Riscos

### Dependências Externas

| Dependência | Descrição | Impacto se Atrasada | Mitigação |
|-------------|-----------|---------------------|-----------|
| **Hermes Gateway** | Disponibilidade para testes modo Hermes (Sprint 2-3) | Bloqueia validação GAP-011, S3-03 | Mock adapter para testes; testar com gateway real apenas em integração final |
| **Aprovações PO/Tech Lead** | Decisões DOM-001 a DOM-008, CON-001 a CON-006 | Bloqueia Sprint 3 itens condicionais | Time-box: decisões até fim da Sprint 1; default = não fazer (YAGNI) |
| **Compliance Review** | Validação AMB-003 (imutabilidade criptográfica eventos) | Bloqueia GAP-010 / S3-06 | Documentar como risk aceito para POC; revisar se produto evoluir |

### Riscos Técnicos

| Risco | Probabilidade | Impacto | Mitigação | Dono |
|-------|---------------|---------|-----------|------|
| **R1**: Ports/Adapters introduz breaking change na API interna | Média | Alto | Testes de contrato (Port validation) + CI; feature flag `CRIVO_ENABLE_ACL` para rollout gradual | Tech Lead |
| **R2**: Circuit Breaker adiciona complexidade no HermesAdapter | Baixa | Médio | Implementação simples (contador + timestamp); testes de caos; observabilidade de estado | Dev |
| **R3**: Performance targets (NFR-004/005) não atingidos | Média | Baixo (POC) | Benchmark cedo (Sprint 2); se falhar, documentar limite real e ajustar target | Dev + QA |
| **R4**: Scope creep em Sprint 3 (Rich Model, CQRS, Auth) | Alta | Médio | Time-box Sprint 3; decisões DOM-001 a DOM-008 pré-requisito; YAGNI por default | PM |
| **R5**: Binário `cloudflared` / segredo `password` no histórico Git | Certa (já público) | Alto (compliance) | Documentado no baseline (GAP-005); não removível; mitigar com rotação de segredos se reais | PM + Security |

---

## 6. Decisões Pendentes (Requerem Aprovação para Sprint 3)

| ID | Pergunta | Opções | Recomendação PM | Aprovador | Prazo |
|----|----------|--------|-----------------|-----------|-------|
| **DOM-001** | Evoluir para Rich Domain Model na Construction? | Sim / Não (manter anêmico) | **Não** — YAGNI para POC; revisar se produto crescer | Tech Lead | Fim Sprint 1 |
| **DOM-002** | Extrair políticas para configuração versionada? | Sim / Não (hardcoded) | **Não** — POC scope; hardcoded = rastreabilidade implícita | PO + Tech Lead | Fim Sprint 1 |
| **DOM-003** | Adotar CQRS (separar read/write)? | Sim / Não | **Não** — Single model suficiente para POC | Tech Lead | Fim Sprint 1 |
| **DOM-004** | Implementar Anti-Corruption Layer explícito para Hermes? | Sim / Não | **Sim** — Baixo custo, alto valor p/ evolução; já especificado no Contract Design | Tech Lead | Fim Sprint 1 |
| **DOM-005** | Adicionar assinatura criptográfica/hashing aos eventos? | Sim / Não | **Não** — POC; compliance não exige hoje; documentar como risk | Compliance | Fim Sprint 1 |
| **DOM-006** | Permitir cenários customizados (entrada livre)? | Sim / Não | **Não** — Segurança (zero dados reais), simplicidade | PO (Rodrigo) | Fim Sprint 1 |
| **DOM-007** | Adicionar identidade de usuário (auth) para multi-tenancy? | Sim / Não | **Não** — Além de POC scope | Tech Lead | Fim Sprint 1 |
| **DOM-008** | `reviewer_simulado` deve retornar `contesta` em algum caso? | Sim / Não | **Não** — Simplificação POC; modelo permite, não usado | PO + Tech Lead | Fim Sprint 1 |
| **CON-001** | Publicar OpenAPI spec em `/api/openapi.yaml` endpoint? | Sim / Não | **Sim** — DX, contract testing; já no Sprint 1 | Tech Lead | Fim Sprint 1 |
| **CON-002** | Adicionar versionamento de API (`/api/v1/...`)? | Sim / Não | **Não** — POC v1.0.0; versionar se breaking changes futuros | Tech Lead | Fim Sprint 1 |
| **CON-003** | Contract testing (Pact) para adapters? | Sim / Não | **Não** — Overhead para POC; validação runtime (Protocol) suficiente | QA | Fim Sprint 1 |
| **CON-004** | Schema registry para eventos (Avro/Protobuf) vs JSON atual? | JSON / Avro / Protobuf | **JSON** — Simplicidade, zero deps, validação JSON Schema suficiente | Tech Lead | Fim Sprint 1 |
| **CON-005** | Validar config com Pydantic/Settings na inicialização? | Sim / Não | **Não** — Zero deps; validação manual em `hermes.configured_adapters()` ok | Tech Lead | Fim Sprint 1 |
| **CON-006** | Definir SLA formal para Hermes (latência, disponibilidade)? | Sim / Não | **Não** — Opt-in, não crítico; documentar targets informais | Tech Lead | Fim Sprint 1 |

---

## 7. Métricas de Sucesso (Construction Phase)

| Métrica | Target | Como Medir | Frequência |
|---------|--------|------------|------------|
| **Test Coverage** | ≥ 90% em `crivo/` | `pytest --cov=crivo --cov-report=term` | Cada PR / Sprint |
| **CI/CD Pass Rate** | 100% em `main` | GitHub Actions badge + history | Contínuo |
| **AC Coverage** | 100% dos 36 ACs validados por testes | Matriz AC → Teste (relatório) | Sprint Review |
| **Performance (NFR-004)** | p99 < 100ms (modo simulado) | Benchmark script (locust/hey) | Sprint 2 + Release |
| **Throughput (NFR-005)** | ≥ 10 req/s concorrentes | Benchmark script | Sprint 2 + Release |
| **Hermes Resilience** | Circuit Breaker abre após 5 falhas; retry 3x com backoff | Testes de integração + chaos | Sprint 2 |
| **Security** | 0 vulnerabilidades `bandit` / `safety` high/critical | CI security scan | Cada PR |
| **Lead Time (PR → Merge)** | < 24h | GitHub Actions / PR timestamps | Sprint Retro |
| **Defect Escape Rate** | 0 bugs em produção (POC local) | QA sign-off | Release |

---

## 8. Próximos Passos Imediatos

1. **Aprovação deste Delivery Planning** — Sign-off PO (Rodrigo) + Tech Lead + QA
2. **Decisões pendentes (Seção 6)** — Time-box: resolver até fim da Sprint 1
3. **Executar approval-handoff (stage 1.6)** — Gate 5: Inception → Construction
4. **Iniciar Sprint 1** — `pyproject.toml` + test suite + CI/CD + OpenAPI endpoint
5. **Atualizar `aidlc-state.md`** — Marcar delivery-planning como concluída, iniciar construction/functional-design

---

## 9. Referências

- Requirements Analysis: `aidlc/spaces/default/intents/261123-crivo-credito-stabilize/inception/requirements-analysis/memory.md`
- Domain Design: `aidlc/spaces/default/intents/261123-crivo-credito-stabilize/inception/domain-design/memory.md`
- Contract Design: `aidlc/spaces/default/intents/261123-crivo-credito-stabilize/inception/contract-design/memory.md`
- ADRs Baseline: `docs/adr/ADR-001` a `ADR-007`
- ADRs Governança: `docs/adr/ADR-008` a `ADR-012`
- Handoff: `/opt/data/projects/crivo-credito-demo/handoff.md`
- AI-DLC State: `aidlc/spaces/default/intents/261123-crivo-credito-stabilize/aidlc-state.md`

---

*Delivery Planning completo. Pronto para Gate 5 (Inception → Construction) após sign-off dos stakeholders e execução de approval-handoff.*