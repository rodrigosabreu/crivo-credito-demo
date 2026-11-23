# Crivo Crédito Demo — AGENTS.md

> **Objetivo**: Ponto de entrada para agentes trabalharem neste projeto. Contém instruções operacionais, stack real, comandos e integração com o Agentic Home.

---

## 🎯 Objetivo do Projeto

POC local de análise de crédito **exclusivamente sintética** — não concede, nega ou recomenda crédito. Simula motor de regras determinísticas com analista e revisor simulados (funções Python locais), com modo opt-in para gateway Hermes. Toda execução exige revisão humana (`revisao_humana: pendente`).

---

## 🛠️ Stack Real Identificada no Código

| Camada | Tecnologia |
|--------|------------|
| **Linguagem** | Python 3.10+ (stdlib only) |
| **HTTP Server** | `http.server.ThreadingHTTPServer` (127.0.0.1:8000) |
| **Banco de Dados** | SQLite (`crivo.sqlite3`) — tabelas `runs` + `events` |
| **Motor de Regras** | `engine.py` — 3 regras versionadas (`politica: demonstrativa-1.0`) |
| **Orquestração** | `service.py` — casos, analista, revisor, persistência, adapters injetáveis |
| **UI** | `index.html` — vanilla JS + fetch API (single-page) |
| **Gateway Hermes (opt-in)** | `hermes.py` — cliente HTTP para gateway local (loopback) |

**Dependências externas**: Nenhuma (apenas stdlib + SQLite). O modo Hermes exige gateway rodando separadamente.

---

## 📁 Estrutura de Diretórios

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
├── demo.py                  # Script alternativo (não usado no demo)
├── test_origin_regression.py
├── verify.py
├── .gitignore
└── README.md
```

---

## 🚀 Comandos de Execução e Testes

### Executar Localmente (modo simulado — padrão)
```bash
cd /opt/data/projects/crivo-credito-demo/crivo
python3 run_server.py
# Servidor em http://127.0.0.1:8000
# UI: http://127.0.0.1:8000/ui
# API: http://127.0.0.1:8000/api/cenarios
```

### Testar via API
```bash
# Listar cenários
curl http://127.0.0.1:8000/api/cenarios

# Executar simulação
curl -X POST http://127.0.0.1:8000/api/execucoes \
  -H "Content-Type: application/json" \
  -d '{"cenario": "completo"}'

# Ver resultado + eventos
curl http://127.0.0.1:8000/api/execucoes/{id}
curl http://127.0.0.1:8000/api/execucoes/{id}/eventos
```

### Cenários Sintéticos Disponíveis
| ID | Título | Descrição |
|----|--------|-----------|
| `completo` | Completo e consistente | Todos os campos presentes, valores válidos, total = valor × parcelas |
| `ausente` | Dados ausentes | Campos `valor` e `total_declarado` são `null` |
| `divergente` | Total divergente | `total_declarado` (900) ≠ `valor` (1000) |
| `violacao` | Parcelas inválidas | `parcelas = 0` (divisão por zero) |

### Modo Hermes (opt-in)
Requer gateway Hermes rodando em loopback com variáveis `CRIVO_HERMES_CHAVE_*`, `CRIVO_HERMES_PORTA`. **Não há fallback automático** — falha → parecer de falha + revisão humana pendente.

---

## 🔒 Regras de Segurança

- **Zero dados reais** — catálogo sintético fixo, sem CPF, sem documentos
- **Regras versionadas e imutáveis** — agentes não alteram resultados do motor (`politica: demonstrativa-1.0`)
- **Concordância ≠ correção** — revisor apenas acompanha regras demonstrativas
- **Human-in-the-loop obrigatório** — estado final sempre `revisao_humana: pendente`
- **Origem rastreada** — `adaptadores.analista/revisor` mostra `simulado_local` ou `adaptador_hermes_..._modelo_nao_verificado`
- **Sem fallback automático** — falha do analista/revisor → revisão humana
- **Não exponha serviços** — roda em `127.0.0.1:8000`; túnel só para demo temporário
- **Sem autenticação/autorização** — POC não endurecida para rede
- **Não validada juridicamente/regulatoriamente** — não usar com dados reais ou decisões efetivas

---

## 🔗 Integração com Agentic Home (Skills Compartilhadas)

Este projeto pode usar as skills compartilhadas do `agentic-home`:

```bash
# No Hermes Agent, carregue skills conforme necessário:
skill_view(name='descoberta')    # Exploração de problemas & requisitos
skill_view(name='arquitetura')   # Design técnico, trade-offs, ADRs
skill_view(name='desenvolvimento') # Padrões de implementação, testes
skill_view(name='qualidade')     # Validação, testes, revisão de código
```

**Templates disponíveis no Home:**
- `agentic-home/templates/handoff.md` — Template de handoff de tarefa (append-only)
- `agentic-home/templates/adr.md` — Template de ADR (decisões arquiteturais)

**Como usar:**
1. Clone o `agentic-home` e leia seu `AGENTS.md`
2. Navegue pelo catálogo: `cat projects/catalogo.md`
3. Carregue skills relevantes antes de iniciar trabalho
4. Crie `handoff.md` na raiz deste projeto para cada tarefa (seguindo template da Home)
5. Atualize o handoff conforme progride (append-only)

---

## 📋 Orientação para Handoffs por Tarefa

Para cada tarefa neste projeto:

1. **Crie/atualize** `handoff.md` na raiz do projeto usando o template: `agentic-home/templates/handoff.md`
2. **Preencha** os campos obrigatórios:
   - Identificador e descrição da tarefa
   - Projeto, Owner, Status
   - Aprovado (decisão, data, aprovador)
   - Aguardando (dependências/bloqueadores)
   - Próxima ação (explícita e executável)
   - Artefatos (caminhos reais)
   - Histórico (append-only)
   - Validação (checks executados, resultados, pendentes)
3. **Não sobrescreva** histórico anterior — apenas apende
4. **Referencie** artefatos reais (caminhos absolutos ou relativos ao repo)
5. **Não marque como aprovado** sem evidência (link para PR, testes, registro de aprovação)

---

## 🤖 AI-DLC Workspace
>
> **Objetivo**: Este projeto integra o AI-DLC (AI Development Lifecycle) para governança, continuidade entre sessões e stage gates com aprovação humana. O workspace AI-DLC é a **source of truth operacional** — o AGENTS.md aponta para ele, não o substitui.
>
> ### Estrutura do Workspace
> ```
> aidlc/
> └── spaces/
>     └── default/
>         ├── intents/
>         │   ├── intents.json                      # Índice de intents
>         │   └── 261123-crivo-credito-stabilize/   # Intent ativo
>         │       ├── aidlc-state.md                # Estado de execução (fase, stage, next action)
>         │       ├── project-description.json      # Descrição canônica do projeto
>         │       ├── ideation/                     # Fase 0 (skipped - brownfield)
>         │       │   ├── intent-capture/memory.md
>         │       │   ├── scope-definition/memory.md
>         │       │   └── approval-handoff/memory.md
>         │       ├── inception/                    # Fase 1 (FOCO ATUAL)
>         │       │   ├── reverse-engineering/memory.md
>         │       │   ├── requirements-analysis/memory.md
>         │       │   ├── domain-design/memory.md
>         │       │   ├── contract-design/memory.md
>         │       │   ├── delivery-planning/memory.md
>         │       │   └── approval-handoff/memory.md
>         │       ├── construction/                 # Fase 2 (futuro)
>         │       └── audit/                        # Trilha de auditoria
>         └── memory/
>             ├── project.md                        # Memória do projeto (decisões, ADRs, contexto)
>             └── phases/
>                 ├── ideation.md
>                 ├── inception.md
>                 ├── construction.md
>                 └── operation.md
> ```
>
> ### Arquivos Principais
> | Arquivo | Finalidade | Localização |
> |---------|------------|-------------|
> | `aidlc-state.md` | Estado operacional: fase, stage, gate status, next action, baseline commit | `aidlc/spaces/default/intents/261123-crivo-credito-stabilize/aidlc-state.md` |
> | `project-description.json` | Descrição canônica do projeto (ID, nome, tipo, escopo, status) | `aidlc/spaces/default/intents/261123-crivo-credito-stabilize/project-description.json` |
> | `project.md` | Memória persistente: decisões, ADRs, gaps, riscos, contexto operacional | `aidlc/spaces/default/memory/project.md` |
> | `intents.json` | Índice de todos os intents do workspace | `aidlc/spaces/default/intents/intents.json` |
> | `handoff.md` | Continuidade entre sessões (estendido com campos AI-DLC) | Raiz do projeto (`/handoff.md`) |
> | ADRs | Decisões arquiteturais (baseline `Implemented` + governança `Proposed`) | `docs/adr/ADR-XXX-*.md` |
>
> ### Stage Gates (Aprovação Humana Obrigatória)
> | Gate | Transição | Aprovador | Status |
> |------|-----------|-----------|--------|
> | Gate 0 | Diagnose → Plan | Rodrigo (PM) | ✅ APROVADO |
> | Gate 1 | Plan → Baseline | Rodrigo (PM) | ✅ APROVADO |
> | Gate 2 | Baseline → Integrate | Rodrigo (PM) | ⏳ PENDENTE |
> | Gate 3 | Integrate → Validate | Rodrigo (PM) | ⏳ PENDENTE |
> | Gate 4 | Validate → Inception | Rodrigo (PM) | ⏳ PENDENTE |
>
> **Regra**: Nenhuma transição de fase ocorre sem aprovação registrada no `approval-handoff/memory.md` correspondente e no `handoff.md`.
>
> ### Recuperação de Contexto (Nova Sessão)
> Para retomar trabalho em nova sessão:
> 1. Leia `handoff.md` na raiz — identifica task, status, next action, aguardando
> 2. Leia `aidlc-state.md` — identifica fase atual, stage atual, gate status, baseline commit
> 3. Leia `project.md` — decisões/ADRs, gaps, riscos, contexto operacional
> 4. Carregue skills necessárias: `skill_view(name='descoberta')`, `skill_view(name='arquitetura')`, `skill_view(name='desenvolvimento')`, `skill_view(name='qualidade')`, `skill_view(name='onboard-ai-dlc')`
> 5. Execute a **Próxima Ação** do handoff
>
> ### Integração com Agentic-Home
> - **Skills**: `descoberta`, `arquitetura`, `desenvolvimento`, `qualidade`, `onboard-ai-dlc` (carregar via `skill_view()`)
> - **Templates**: `agentic-home/templates/handoff.md`, `agentic-home/templates/adr.md` (estendidos com campos AI-DLC)
> - **Catálogo**: `agentic-home/projects/catalogo.md` (entrada `crivo-credito-demo` registrada)
> - **Governança**: `agentic-home/docs/governanca.md` (stage gates, matriz de permissões)
> - **Onboarding**: `agentic-home/docs/onboarding.md`
>
> ---

## 📚 Documentação Relacionada

| Documento | Localização |
|-----------|-------------|
| README completo | `README.md` |
| Catálogo do Agentic Home | `agentic-home/projects/catalogo.md` |
| Skills compartilhadas | `agentic-home/skills/` |
| Template de handoff | `agentic-home/templates/handoff.md` |
| Template de ADR | `agentic-home/templates/adr.md` |

---

*Este AGENTS.md é a fonte de verdade para agentes operando neste projeto. Atualize quando houver mudanças na stack, comandos, estrutura ou regras.*