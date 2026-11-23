# Integration Plan — Crivo Crédito Demo

**Data**: 2026-11-23
**Projeto**: crivo-credito-demo
**Caminho**: /opt/data/projects/crivo-credito-demo
**Tipo**: brownfield
**Diagnose Report**: `diagnose-report.md` (aprovado)
**Intent ID**: `261123-crivo-credito-stabilize`

---

## 1. Estratégia de Integração

### Estratégia Escolhida: **Brownfield Integration**
Integrar AI-DLC preservando todo o código, histórico Git e estrutura existente. Nenhum arquivo funcional do projeto será modificado — apenas arquivos de governança (AI-DLC workspace, ADRs, handoff, AGENTS.md) serão criados/atualizados.

### Abordagem por Fases (conforme skill `onboard-ai-dlc`):
1. **Diagnose** ✅ Concluído e aprovado
2. **Plan** 📋 Este documento
3. **Baseline** — Capturar commit HEAD, registrar decisões históricas como ADRs `Implemented`
4. **Integrate** — Criar estrutura `aidlc/`, arquivos principais, stage memories, ADRs, handoff, atualizar AGENTS.md
5. **Validate** — Testar recuperação de contexto, idempotência, rollback, gates, integração Home

---

## 2. Arquivos a Criar, Modificar e Preservar

### 2.1 Arquivos a Criar (Estrutura `aidlc/` Completa)

```
aidlc/
└── spaces/
    └── default/
        ├── intents/
        │   ├── intents.json                           # Índice de intents
        │   └── 261123-crivo-credito-stabilize/        # Intent directory
        │       ├── aidlc-state.md                     # Estado de execução
        │       ├── project-description.json           # Descrição canônica
        │       ├── ideation/                          # Fase 0 (SKIP - brownfield)
        │       │   ├── intent-capture/
        │       │   │   └── memory.md
        │       │   ├── scope-definition/
        │       │   │   └── memory.md
        │       │   └── approval-handoff/
        │       │       └── memory.md
        │       ├── inception/                         # Fase 1 (FOCO)
        │       │   ├── reverse-engineering/
        │       │   │   └── memory.md
        │       │   ├── requirements-analysis/
        │       │   │   └── memory.md
        │       │   ├── domain-design/
        │       │   │   └── memory.md
        │       │   ├── contract-design/
        │       │   │   └── memory.md
        │       │   ├── delivery-planning/
        │       │   │   └── memory.md
        │       │   └── approval-handoff/
        │       │           └── memory.md
        │       ├── construction/                      # Fase 2 (futuro)
        │       └── audit/                             # Trilha de auditoria
        └── memory/
            ├── project.md                             # Memória do projeto
            └── phases/
                ├── ideation.md
                ├── inception.md
                ├── construction.md
                └── operation.md
```

### 2.2 Arquivos a Modificar

| Arquivo | Modificação | Justificativa |
|---------|-------------|---------------|
| `AGENTS.md` | Adicionar seção **AI-DLC Workspace** com referências a `aidlc/`, skills, templates, stage gates, instruções de recuperação de contexto | Integração obrigatória AI-DLC |
| `handoff.md` (novo) | Criar handoff inicial seguindo template `agentic-home/templates/handoff.md` estendido com campos AI-DLC (phase, stage, gate status, phase gate status) | Continuidade entre sessões |

### 2.3 Arquivos a Preservar (Não Modificar)

| Arquivo/Diretório | Razão |
|-------------------|-------|
| `crivo/` (todo o package) | Código funcional — preservar 100% |
| `demo.py`, `test_origin_regression.py`, `verify.py` | Scripts de teste existentes |
| `README.md` | Documentação existente (pode ser referenciada) |
| `.gitignore` | Configuração existente |
| `crivo.sqlite3`, `demo.sqlite3` | Bancos de dados (ignorados pelo git) |
| `cloudflared`, `password` | Binários/segredos (já no .gitignore, mantidos como estão) |
| Git history (6 commits) | Histórico imutável |

---

## 3. Stage Gates e Aprovações

### 3.1 Gates Obrigatórios (Baseado em `agentic-home/docs/governanca.md`)

| Gate | Transição | Aprovador | Critérios de Aprovação |
|------|-----------|-----------|------------------------|
| **Gate 0** | Diagnose → Plan | Rodrigo (PM) | Diagnose report aprovado, classificação confirmada, gaps/risks validados |
| **Gate 1** | Plan → Baseline | Rodrigo (PM) | Integration plan aprovado, stage gates definidos, rollback testável |
| **Gate 2** | Baseline → Integrate | Rodrigo (PM) | Baseline commit capturado, ADRs históricos `Implemented`, gaps documentados |
| **Gate 3** | Integrate → Validate | Rodrigo (PM) | Estrutura `aidlc/` completa, arquivos principais criados, AGENTS.md atualizado, handoff criado |
| **Gate 4** | Validate → Inception (reverse-engineering) | Rodrigo (PM) | Validation report APROVADO: recuperação 100%, idempotência, rollback, gates funcionais |

### 3.2 Aprovadores por Papel

| Papel | Responsável | Contato |
|-------|-------------|---------|
| **Product Owner / PM** | Rodrigo | Decisões de negócio, priorização, gates de fase |
| **Tech Lead** | (a definir) | Decisões técnicas, arquitetura, ADRs |
| **QA Lead** | (a definir) | Validação, testes, quality gates |

> **Nota**: Para este projeto brownfield, Rodrigo atua como PM e aprovador único dos gates 0-4. Tech Lead e QA serão envolvidos na fase Inception.

### 3.3 Template de Aprovação
Usar `agentic-home/templates/handoff.md` estendido com campos AI-DLC + `references/approval-handoff-template.md` para gates de fase.

---

## 4. Critérios de Aceite por Fase

### Fase 2: Plan (Este Documento)
- [ ] Plano completo e acionável gerado
- [ ] Stage gates definidos com aprovadores
- [ ] Critérios de aceite mensuráveis por fase
- [ ] Plano de rollback testável
- [ ] Riscos mapeados com mitigações
- [ ] Cronograma estimado

### Fase 3: Baseline
- [ ] Baseline Git capturado corretamente (commit HEAD: `82c9900`)
- [ ] ADRs históricos criados com status `Implemented`
- [ ] Nenhuma aprovação retroativa inventada
- [ ] Gaps e pendências documentados
- [ ] `aidlc-state.md` atualizado com baseline commit
- [ ] `project.md` atualizado com decisões baseline

### Fase 4: Integrate
- [ ] Estrutura `aidlc/` criada completa (idempotente)
- [ ] Todos arquivos principais criados: `aidlc-state.md`, `project-description.json`, `project.md`, `intents.json`
- [ ] Stage memories criados para Inception (reverse-engineering, requirements-analysis, domain-design, contract-design, delivery-planning, approval-handoff)
- [ ] ADRs criados/atualizados (baseline + novos)
- [ ] `handoff.md` criado/atualizado com campos AI-DLC
- [ ] `AGENTS.md` atualizado com seção AI-DLC Workspace
- [ ] Stage gates configurados (approval-handoff memories)
- [ ] Nenhum arquivo funcional do projeto modificado
- [ ] Idempotência: executar duas vezes não duplica arquivos

### Fase 5: Validate
- [ ] Recuperação de contexto 100% funcional (simular nova sessão)
- [ ] Idempotência comprovada (execução dupla idêntica)
- [ ] Rollback funcional (simular falha, restaurar estado anterior)
- [ ] Stage gates bloqueiam corretamente
- [ ] Integração Agentic-Home funcional (skills carregáveis, templates referenciam Home)
- [ ] Relatório de validação completo com status APROVADO

---

## 5. Plano de Rollback

### 5.1 Procedimento por Fase

| Fase | Procedimento de Rollback | Arquivos a Restaurar | Comando Git |
|------|--------------------------|---------------------|-------------|
| **Plan** | Nenhum arquivo criado — apenas documento | N/A | N/A |
| **Baseline** | Remover ADRs baseline criados, restaurar `aidlc-state.md` e `project.md` pré-baseline | ADRs baseline, `aidlc-state.md`, `project.md` | `git checkout HEAD -- aidlc/` (se commitado) ou `rm -rf aidlc/` |
| **Integrate** | Remover diretório `aidlc/` inteiro, restaurar `AGENTS.md` e `handoff.md` originais | `aidlc/`, `AGENTS.md`, `handoff.md` | `git checkout HEAD -- aidlc/ AGENTS.md handoff.md` ou `rm -rf aidlc/ && git checkout HEAD -- AGENTS.md handoff.md` |
| **Validate** | Mesmo que Integrate | Mesmo que Integrate | Mesmo que Integrate |

### 5.2 Pontos de Verificação (Checkpoints)
- **Pre-Baseline**: Tag `pre-ai-dlc-baseline` = commit `82c9900`
- **Post-Baseline**: Tag `post-ai-dlc-baseline` = após Baseline workflow
- **Post-Integrate**: Tag `post-ai-dlc-integrate` = após Integrate workflow
- **Post-Validate**: Tag `post-ai-dlc-validate` = após Validate workflow

### 5.3 Comando de Rollback Completo (Emergência)
```bash
cd /opt/data/projects/crivo-credito-demo
git checkout pre-ai-dlc-baseline  # Restaura estado pré-AI-DLC
# OU
git reset --hard 82c9900 && rm -rf aidlc/  # Hard reset + limpeza
```

---

## 6. Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| **Binários/segredos no repo** | Alta | Médio | Documentar no baseline; adicionar ao `.gitignore` se não estiver; não remover do histórico (já comittado) |
| **Conflito AGENTS.md vs AI-DLC state** | Média | Médio | Unificar referências: AGENTS.md aponta para `aidlc/` como source of truth operacional |
| **Templates ADR/handoff divergentes** | Baixa | Baixo | Estender templates Home, não copiar; referenciar `agentic-home/templates/` |
| **Stage gates não respeitados** | Baixa | Alto | Validação automática em Validate; gates impedem avanço sem aprovação registrada |
| **Perda de contexto entre sessões** | Baixa | Alto | Teste de recuperação obrigatório em Validate; handoff.md + aidlc-state.md sincronizados |
| **Dependências não aprovadas** | Média | Bloqueador | Verificação em Plan/Integrate: todos gates têm aprovador definido |
| **Conflito de skills (namespace)** | Baixa | Baixo | Namespace `agentic-home:` vs projeto; skills Home carregadas via `skill_view()` |
| **Perda de histórico Git** | Baixa | Crítico | Rollback testado, tags criadas, Git history preservado |
| **Idempotência falha** | Baixa | Médio | Teste duplo em Validate; estrutura verificada byte-a-byte |

---

## 7. Cronograma Estimado

| Fase | Duração Estimada | Dependências |
|------|------------------|--------------|
| **Plan** | 30 min | Diagnose aprovado ✅ |
| **Baseline** | 45 min | Plan aprovado (Gate 1) |
| **Integrate** | 60 min | Baseline aprovado (Gate 2) |
| **Validate** | 45 min | Integrate aprovado (Gate 3) |
| **Total** | **~3 horas** | Gates sequenciais com aprovação humana |

> **Nota**: Estimativa para execução por agente único. Gates requerem aprovação humana (Rodrigo) — tempo de espera não incluído.

---

## 8. ADRs a Criar (Baseline + Novos)

### 8.1 ADRs Baseline (Status: `Implemented` — decisões já implementadas no código)

| ADR ID | Título | Descrição | Fonte |
|--------|--------|-----------|-------|
| ADR-001 | Stack tecnológica Python 3.10+ stdlib + SQLite | Linguagem, server HTTP, banco de dados | Código (`engine.py`, `service.py`, `server.py`) |
| ADR-002 | Arquitetura em camadas: Engine → Service → Server → Adapters | Separação de responsabilidades, injeção de dependência | Código (`engine.py`, `service.py`, `hermes.py`) |
| ADR-003 | Motor determinístico versionado `politica: demonstrativa-1.0` | Regras imutáveis, não alteradas por agentes | Código (`engine.py`) |
| ADR-004 | Event Sourcing para auditoria (tabela `events`) | Trilha imutável: cenario → regras → analista → revisor → revisao_humana | Código (`service.py`, `engine.py`) |
| ADR-005 | Human-in-the-loop obrigatório (estado final `revisao_humana: pendente`) | Nenhuma decisão automática final | Código (`service.py`) |
| ADR-006 | Security-first: loopback only, origin validation, CSRF protection | Bind 127.0.0.1:8000, validação de origem | Código (`server.py`, `demo.py`) |
| ADR-007 | Dois modos de execução: simulado (padrão) e hermes (opt-in) | Adapters injetáveis via env `CRIVO_MODO` | Código (`service.py`, `hermes.py`) |

### 8.2 ADRs Novos (Status: `Proposed` — decisões de governança AI-DLC)

| ADR ID | Título | Descrição |
|--------|--------|-----------|
| ADR-008 | Adoção do AI-DLC workspace no projeto | Estrutura `aidlc/`, stage gates, handoff, memória persistente |
| ADR-009 | Stage gates com aprovação humana obrigatória | Gates Ideation→Inception, Inception→Construction, Construction→Operation |
| ADR-010 | Integração com Agentic-Home (skills, templates, catálogo) | Skills descoberta, arquitetura, desenvolvimento, qualidade |
| ADR-011 | Handoff.md estendido com campos AI-DLC | Phase, stage, gate status, phase gate status, intent ID |
| ADR-012 | Baseline de decisões históricas como ADRs `Implemented` | Sem aprovação retroativa; registrar como baseline histórico |

---

## 9. Intent Definition

```json
{
  "id": "261123-crivo-credito-stabilize",
  "name": "Crivo Crédito Demo Stabilization",
  "description": "Integrar AI-DLC ao Crivo Crédito Demo (brownfield) para governança, continuidade e stage gates com aprovação humana",
  "projectRoot": "/opt/data/projects/crivo-credito-demo",
  "projectType": "brownfield",
  "scope": "project",
  "startDate": "2026-11-23T00:00:00Z",
  "status": "plan",
  "activeStage": "approval-handoff (Plan → Baseline gate)"
}
```

---

## 10. Próximos Passos e Responsáveis

| Ação | Responsável | Prazo | Gate |
|------|-------------|-------|------|
| Revisar e aprovar Integration Plan | Rodrigo (PM) | Imediato | Gate 1 (Plan → Baseline) |
| Executar Baseline workflow | Agente (Polaris/Atlas) | Pós-Gate 1 | Gate 2 (Baseline → Integrate) |
| Executar Integrate workflow | Agente (Polaris/Atlas) | Pós-Gate 2 | Gate 3 (Integrate → Validate) |
| Executar Validate workflow | Agente (Polaris/Atlas) | Pós-Gate 3 | Gate 4 (Validate → Inception) |

---

## 11. Aprovação Necessária

Este plano de integração deve ser revisado e aprovado antes de prosseguir para o **Workflow 3: Baseline**.

**Aprovador**: Rodrigo (conforme governança Agentic-Home)
**Critério**: Confirmação da estratégia brownfield, validação dos arquivos a criar/modificar/preservar, stage gates definidos com aprovadores, critérios de aceite mensuráveis, plano de rollback testável, riscos mapeados.

---

*Plano gerado conforme Workflow 2: Plan da skill `onboard-ai-dlc` v1.0.0*
*Baseado em: `diagnose-report.md` (aprovado)*