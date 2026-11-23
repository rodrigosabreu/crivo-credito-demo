# Diagnose Report — Crivo Crédito Demo

**Data**: 2026-11-23
**Projeto**: crivo-credito-demo
**Caminho**: /opt/data/projects/crivo-credito-demo
**Tipo Solicitado**: brownfield
**Classificação Confirmada**: brownfield

---

## 1. Classificação do Projeto

| Critério | Avaliação |
|----------|-----------|
| **Código existente** | Sim — 6 arquivos Python principais + HTML + testes |
| **Histórico Git** | Sim — 6 commits na branch `main` |
| **AI-DLC workspace (`aidlc/`)** | Não existe |
| **ADRs** | Não existem |
| **Handoff.md** | Não existe |
| **Stage gates** | Não configurados |

**Conclusão**: Projeto **brownfield** — código funcional existente, sem AI-DLC. Requer integração preservando histórico e código.

---

## 2. Stack Tecnológica Identificada

| Camada | Tecnologia | Detalhes |
|--------|------------|----------|
| **Linguagem** | Python 3.10+ | Apenas stdlib + SQLite |
| **HTTP Server** | `http.server.ThreadingHTTPServer` | Bind `127.0.0.1:8000` |
| **Banco de Dados** | SQLite (`crivo.sqlite3`) | Tabelas `runs` + `events` |
| **Motor de Regras** | `engine.py` | 3 regras versionadas (`politica: demonstrativa-1.0`) |
| **Orquestração** | `service.py` | Casos, analista, revisor, persistência, adapters injetáveis |
| **UI** | `index.html` | Vanilla JS + fetch API (single-page) |
| **Gateway Hermes (opt-in)** | `hermes.py` | Cliente HTTP para gateway local (loopback) |
| **Testes** | Scripts Python customizados | `demo.py`, `test_origin_regression.py`, `verify.py` |
| **Túnel Demo** | `cloudflared` (binário) | 40MB committed no repo |

**Dependências externas**: Nenhuma (apenas stdlib + SQLite). Modo Hermes exige gateway rodando separadamente.

---

## 3. Arquitetura e Padrões Identificados

### Estrutura de Diretórios
```
crivo-credito-demo/
├── crivo/
│   ├── __init__.py          # "POC local, exclusivamente sintética."
│   ├── engine.py            # Motor determinístico (regras + cálculo)
│   ├── service.py           # Orquestração: casos, analista, revisor, persistência
│   ├── server.py            # HTTP server (ThreadingHTTPServer, 127.0.0.1:8000)
│   ├── hermes.py            # Cliente opcional gateway Hermes (opt-in)
│   ├── index.html           # UI single-page (vanilla JS, fetch API)
│   └── run_server.py        # Entry point (sys.path fix)
├── demo.py                  # Script alternativo (integração com cloudflared + auth)
├── test_origin_regression.py
├── verify.py
├── .gitignore
└── README.md
```

### Padrões Arquiteturais
- **Separação de responsabilidades**: Engine (regras) → Service (orquestração) → Server (HTTP) → Adapters (analista/revisor)
- **Injeção de dependência**: Adapters `analyst_simulado`/`reviewer_simulado` vs `HermesAdapter` (opt-in via env `CRIVO_MODO=hermes`)
- **Motor determinístico versionado**: `politica: demonstrativa-1.0` — regras imutáveis, não alteradas por agentes
- **Event Sourcing para auditoria**: Tabela `events` com trilha imutável* (`cenario_selecionado → regras_executadas → analista → revisor → revisao_humana_necessaria`)
- **Human-in-the-loop obrigatório**: Estado final sempre `revisao_humana: pendente`
- **Security-first**: Loopback only, origin validation, CSRF protection (em `demo.py`), sem autenticação no modo simples

### Modos de Execução
| Modo | Analista | Revisor | Dependências |
|------|----------|---------|--------------|
| **simulado** (padrão) | Função Python local | Função Python local | Nenhuma (stdlib + SQLite) |
| **hermes** (opt-in) | HTTP → Gateway Hermes (`crivo-analista`) | HTTP → Gateway Hermes (`crivo-revisor`) | Gateway rodando em loopback, `CRIVO_HERMES_CHAVE_*`, `CRIVO_HERMES_PORTA` |

---

## 4. Mecanismos de Governança Existentes

| Mecanismo | Status | Observações |
|-----------|--------|-------------|
| **AGENTS.md** | ✅ Existe | Completo: stack, comandos, segurança, integração Agentic Home |
| **README.md** | ✅ Existe | Diagramas Mermaid (arquitetura, container view, sequence), fluxo completo, segurança |
| **Handoff.md** | ❌ Ausente | Necessário para continuidade entre sessões |
| **ADRs** | ❌ Ausentes | Nenhuma decisão arquitetural documentada formalmente |
| **CI/CD** | ❌ Ausente | Sem GitHub Actions, GitLab CI, etc. |
| **Testes Automatizados** | ⚠️ Parcial | Scripts customizados (`demo.py`, `verify.py`, `test_origin_regression.py`) mas sem framework padrão (pytest/unittest) |
| **Dependency Management** | ❌ Ausente | Sem `requirements.txt`, `pyproject.toml`, `setup.py` |
| **Code Quality** | ❌ Ausente | Sem linter, formatter, type checker configurados |

---

## 5. Mecanismos de Memória/Continuidade

| Mecanismo | Status | Observações |
|-----------|--------|-------------|
| **handoff.md** | ❌ Ausente | Template disponível em `agentic-home/templates/handoff.md` |
| **PROGRESSO.md / CHANGELOG.md** | ❌ Ausentes | |
| **ADRs** | ❌ Ausentes | Template disponível em `agentic-home/templates/adr.md` |
| **Documentação de Onboarding** | ✅ Parcial | AGENTS.md serve como ponto de entrada |
| **Git History** | ✅ Existe | 6 commits, branch `main`, limpo |

---

## 6. Gaps em Relação ao AI-DLC Padrão

| Componente AI-DLC | Status Atual | Gap |
|-------------------|--------------|-----|
| `aidlc/` workspace | ❌ Não existe | Estrutura completa necessária |
| `aidlc-state.md` | ❌ Não existe | Estado de execução (fase, stage, next action) |
| `project-description.json` | ❌ Não existe | Descrição canônica do projeto |
| `project.md` (memória) | ❌ Não existe | Decisões, ADRs, contexto persistente |
| `intents.json` + intent dirs | ❌ Não existe | Rastreamento de intenções |
| Stage Memories (ideation/inception/construction) | ❌ Não existe | Observações, tradeoffs, desvios por estágio |
| ADRs (baseline + novas) | ❌ Não existe | Decisões arquiteturais com status e aprovação |
| Stage Gates (approval-handoff) | ❌ Não existe | Gates obrigatórios com aprovação humana |
| Handoff.md estendido AI-DLC | ❌ Não existe | Campos: phase, stage, gate status, phase gate status |
| AGENTS.md com seção AI-DLC | ⚠️ Parcial | Tem integração Agentic Home, mas sem seção AI-DLC Workspace |
| Integração com Skills Home | ✅ Referenciada | AGENTS.md menciona skills descoberta, arquitetura, desenvolvimento, qualidade |

---

## 7. Riscos Identificados

| Risco | Probabilidade | Impacto | Descrição |
|-------|---------------|---------|-----------|
| **Binários e segredos no repo** | Alta | Médio | `cloudflared` (40MB), `password` (arquivo de segredo), `demo.sqlite3` comittados — violam `.gitignore` e boas práticas |
| **Ausência de CI/CD** | Alta | Médio | Sem validação automática de testes, lint, build em PRs |
| **Testes dependentes de infra externa** | Média | Médio | `demo.py` e `verify.py` exigem `cloudflared` rodando e túnel ativo |
| **Sem gerenciamento de dependências** | Média | Baixo | Apenas stdlib hoje, mas futuro pode exigir deps externas sem controle |
| **Conflito AGENTS.md vs AI-DLC state** | Média | Médio | Dois pontos de verdade para contexto operacional |
| **Stage gates não respeitados** | Baixa | Alto | Sem gates, decisões irreversíveis podem ser tomadas sem aprovação |
| **Perda de contexto entre sessões** | Baixa | Alto | Sem handoff.md e aidlc-state.md, recuperação depende de memória do agente |
| **Rollback de integração AI-DLC** | Baixa | Crítico | Se integração falhar, precisa de procedimento testado para restaurar estado anterior |

---

## 8. Recomendação de Estratégia

**Estratégia**: **Brownfield Integration** — Integrar AI-DLC preservando código/histórico existente.

**Abordagem por Fases** (conforme workflows da skill `onboard-ai-dlc`):

1. **Diagnose** ✅ (este relatório)
2. **Plan** — Definir arquivos a criar/modificar, stage gates, critérios de aceite, rollback
3. **Baseline** — Capturar commit HEAD, registrar decisões históricas como ADRs `Implemented` (sem aprovação retroativa), documentar gaps
4. **Integrate** — Criar estrutura `aidlc/`, arquivos principais, stage memories, ADRs, handoff, atualizar AGENTS.md, configurar gates
5. **Validate** — Testar recuperação de contexto, idempotência, rollback, gates, integração Home

**Próximo Passo**: Executar **Workflow 2: Plan** com base neste diagnóstico.

---

## 9. Evidências Coletadas

- AGENTS.md lido completamente (160 linhas)
- README.md lido completamente (293 linhas, diagramas Mermaid)
- Código fonte: `engine.py`, `service.py`, `server.py`, `hermes.py`, `run_server.py`, `__init__.py`
- Testes: `demo.py`, `test_origin_regression.py`, `verify.py`
- Git log: 6 commits, branch `main`, working tree clean
- `.gitignore` verificado (ignora binários, SQLite, segredos, Python cache)
- Estrutura de diretórios mapeada
- Nenhum `aidlc/`, ADRs, handoff.md, CI/CD encontrado

---

## 10. Aprovação Necessária

Este relatório de diagnóstico deve ser revisado e aprovado antes de prosseguir para o **Workflow 2: Plan**.

**Aprovador**: Rodrigo (conforme governança Agentic-Home)
**Critério**: Confirmação da classificação brownfield, validação dos gaps e riscos, autorização para prosseguir com Plan.

---

*Relatório gerado conforme Workflow 1: Diagnose da skill `onboard-ai-dlc` v1.0.0*