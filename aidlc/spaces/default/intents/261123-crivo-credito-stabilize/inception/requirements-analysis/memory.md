# Requirements Analysis — Memory

> **Stage**: requirements-analysis | **Phase**: inception | **Intent**: 261123-crivo-credito-stabilize
> **Date**: 2026-11-23 | **Agent**: Polaris (PM)

---

## Problem Statement

O **Crivo Crédito Demo** é uma POC local de análise de crédito **exclusivamente sintética** que simula um motor de regras determinísticas versionado (`politica: demonstrativa-1.0`) com orquestração de casos, analista e revisor simulados, persistência SQLite com Event Sourcing para auditoria, e interface web single-page. O sistema **não concede, nega ou recomenda crédito** — toda execução exige revisão humana (`revisao_humana: pendente`).

**Público impactado**: Desenvolvedores, QA, analistas de negócio, compliance, stakeholders de produto que precisam validar fluxos de decisão de crédito em ambiente controlado.

---

## Stakeholders

| Papel | Nome/Time | Interesse |
|-------|-----------|-----------|
| **Product Owner** | Rodrigo Abreu (PM) | Governança, stage gates, entrega de valor, compliance |
| **Tech Lead** | TBD | Arquitetura, qualidade técnica, dívida técnica, CI/CD |
| **QA** | TBD | Testabilidade, critérios de aceite, validação de regras |
| **Compliance/Segurança** | TBD | Auditoria, human-in-the-loop, zero dados reais, LGPD |
| **Desenvolvedores** | Time de engenharia | Manutenibilidade, extensibilidade, DX |
| **Usuários da Demo** | Analistas, stakeholders | UI funcional, cenários claros, trilha de auditoria |

---

## Requisitos

### Funcionais

| ID | Requisito | Descrição | Fonte | Componente |
|----|-----------|-----------|-------|------------|
| **REQ-001** | Catálogo de cenários sintéticos fixos | Sistema deve oferecer 4 cenários pré-definidos: `completo`, `ausente`, `divergente`, `violacao` com dados imutáveis | `service.py:9-14`, `engine.py` | `service.CASES`, `engine.evaluate` |
| **REQ-002** | Motor de regras determinístico versionado | Avaliar 3 regras versionadas (`politica: demonstrativa-1.0`): presença, positividade, consistência aritmética | `engine.py:4-12` | `engine.evaluate` |
| **REQ-003** | Cálculo de valor por parcela | Divisão simples `valor / parcelas` (sem juros) quando valores válidos; `null` caso contrário | `engine.py:12` | `engine.evaluate` |
| **REQ-004** | Analista simulado | Gerar parecer conclusivo (`status: "concluido"`) listando inconsistências ou confirmando ausência | `service.py:20-22` | `analyst_simulado` |
| **REQ-005** | Revisor simulado | Gerar veredito: `concorda` (sem issues), `inconclusivo` (com issues), nunca `contesta` na implementação atual | `service.py:24-26` | `reviewer_simulado` |
| **REQ-006** | Human-in-the-loop obrigatório | Estado final **sempre** `revisao_humana: pendente`; sistema não decide | `service.py:59`, `README.md` | `service.run` |
| **REQ-007** | Rastreabilidade de origem dos adaptadores | Identificar se analista/revisor vieram de `simulado_local` ou `adaptador_hermes_..._modelo_nao_verificado` | `service.py:43-47` | `service.run`, `origins` |
| **REQ-008** | Persistência de execução (runs) | Armazenar resultado completo (JSON) em tabela `runs` com UUID | `service.py:58-64` | `service.run`, SQLite |
| **REQ-009** | Event Sourcing para auditoria | Registrar trilha imutável de eventos: `cenario_selecionado`, `regras_executadas`, `analista`, `revisor`, `revisao_humana_necessaria` | `service.py:34-60`, `service.py:71-73` | `events` table, `service.events` |
| **REQ-010** | API REST: Listar cenários | `GET /api/cenarios` → lista de cenários sintéticos com `id`, `titulo`, `simulacao: true` | `server.py:28` | `server.py` |
| **REQ-011** | API REST: Executar simulação | `POST /api/execucoes` com `{cenario: string}` → `201 Created` + resultado completo | `server.py:38-58` | `server.py`, `service.run` |
| **REQ-012** | API REST: Consultar execução | `GET /api/execucoes/{id}` → resultado completo ou 404 | `server.py:30-36` | `server.py`, `service.get_run` |
| **REQ-013** | API REST: Consultar eventos | `GET /api/execucoes/{id}/eventos` → trilha de auditoria ordenada | `server.py:30-36` | `server.py`, `service.events` |
| **REQ-014** | UI Single-Page | Interface web vanilla JS: seleção de cenário, execução, exibição de resultado + trilha | `index.html` | `index.html`, `server.py:27` |
| **REQ-015** | Modo simulado (padrão) | Execução sem dependências externas; analista/revisor = funções Python locais | `hermes.py:86-88`, `service.py:31` | `hermes.configured_adapters`, `service.run` |
| **REQ-016** | Modo Hermes (opt-in) | Execução via gateway Hermes local com perfis `crivo-analista`/`crivo-revisor`; variáveis `CRIVO_HERMES_CHAVE_*`, `CRIVO_HERMES_PORTA` | `hermes.py:25-83`, `hermes.py:86-93` | `HermesAdapter`, `hermes.configured_adapters` |
| **REQ-017** | Falha do adaptador → revisão humana | Erro no analista/revisor (simulado ou Hermes) → parecer de falha + revisor não executado/ falha + `revisao_humana: pendente` | `service.py:37-56` | `service.run` |
| **REQ-018** | Validação de entrada da API | Rejeitar payload inválido (não JSON, chaves duplicadas, tamanho > 1KB, campos inesperados) | `server.py:9-15`, `server.py:50-56` | `server.py`, `unique_keys` |
| **REQ-019** | Origin validation (CSRF básico) | Permitir apenas `localhost:8000`, `127.0.0.1:8000`, origens HTTPS (túneis); bloquear outras | `server.py:42-49` | `server.py` |

### Não-Funcionais

| ID | Requisito | Descrição | Métrica/Target | Componente |
|----|-----------|-----------|----------------|------------|
| **NFR-001** | Determinismo | Mesma entrada → mesmo resultado (motor, analista, revisor simulados) | 100% reprodutível | `engine.py`, `service.py` |
| **NFR-002** | Zero dependências externas (modo padrão) | Apenas Python 3.10+ stdlib + SQLite | `pip list` vazio | Todo o projeto |
| **NFR-003** | Isolamento de rede | Bind apenas em `127.0.0.1:8000`; sem exposição externa | `server.py:59` | `server.py` |
| **NFR-004** | Latência da API (modo simulado) | Execução completa < 100ms (p99) em hardware padrão | < 100ms p99 | `service.run`, `server.py` |
| **NFR-005** | Throughput (modo simulado) | Suportar ≥ 10 req/s concorrentes (ThreadingHTTPServer) | ≥ 10 req/s | `ThreadingHTTPServer` |
| **NFR-006** | Armazenamento | SQLite single-file (`crivo.sqlite3`); tabelas `runs` + `events` | Crescimento linear | SQLite |
| **NFR-007** | Auditoria | Event Sourcing: todo passo rastreado com timestamp UTC, sequência, detalhes JSON | 100% cobertura | `events` table |
| **NFR-008** | Segurança: Zero dados reais | Catálogo sintético fixo; sem CPF, documentos, PII | 0 dados reais | `service.CASES`, `engine.py` |
| **NFR-009** | Segurança: Validação de entrada | Payload ≤ 1KB, JSON válido, chaves únicas, campo único `cenario` | 100% rejeição inválidos | `server.py:50-56` |
| **NFR-010** | Segurança: Origin validation | Bloqueio de origens não permitidas (CSRF básico) | 100% bloqueio | `server.py:42-49` |
| **NFR-011** | Segurança: Headers HTTP | `Cache-Control: no-store`, `X-Content-Type-Options: nosniff` | Presentes em todas respostas | `server.py:24` |
| **NFR-012** | Observabilidade | Logs de erro apenas; trilha de eventos via API `/eventos` | Eventos queryable | `service.events` |
| **NFR-013** | Portabilidade | Python 3.10+ stdlib only; roda em Linux/macOS/Windows sem instalação | Zero setup | Todo o projeto |
| **NFR-014** | Modo Hermes: Timeout | Requisição ao gateway ≤ 15s; resposta ≤ 32KB; prompt ≤ 16KB | `TIMEOUT=15`, `MAX_RESPONSE=32768` | `hermes.py:7-9` |
| **NFR-015** | Modo Hermes: Validação de resposta | Verificar envelope Hermes (`completed=true`, `partial=false`, `failed=false`, `finish_reason=stop`) | 100% validação | `hermes.py:57-76` |
| **NFR-016** | Modo Hermes: Não vazamento de segredos | Rejeitar resposta que contenha `CRIVO_HERMES_CHAVE_*` | 0 vazamentos | `hermes.py:78-80` |
| **NFR-017** | Conformidade: Não decisão de crédito | Aviso explícito em toda resposta: `"Simulação exclusivamente sintética. Não é decisão de crédito."` | 100% respostas | `service.py:59` |
| **NFR-018** | Conformidade: Human-in-the-loop | Estado final sempre `revisao_humana: pendente`; nunca `aprovado`/`negado` | 100% execuções | `service.py:59` |
| **NFR-019** | Manutenibilidade: Injeção de dependência | Analista e revisor injetáveis em `service.run` para testes e modo Hermes | DI funcional | `service.py:31` |
| **NFR-020** | Versionamento de política | `politica: demonstrativa-1.0` imutável no código; alteração = nova versão | Versionamento explícito | `engine.py:1` |

---

## Cenários

### Caminho Feliz (Cenário `completo`)

1. Usuário acessa `http://127.0.0.1:8000/ui`
2. UI carrega lista de cenários via `GET /api/cenarios`
3. Usuário seleciona `completo` e clica "Executar simulação"
4. UI envia `POST /api/execucoes` com `{"cenario": "completo"}`
5. Servidor valida origin, payload, chama `service.run(db, "completo")`
6. Motor avalia 3 regras → todas `observado`
7. Analista simulado retorna `concluido` + "nenhuma inconsistência..."
8. Revisor simulado retorna `concorda` + "acompanha regras..."
9. Resultado persistido em `runs` + 5 eventos em `events`
10. API retorna `201` + JSON completo com `revisao_humana: pendente`
11. UI busca eventos via `GET /api/execucoes/{id}/eventos`
12. UI exibe cenário, regras, valor/parcela, pareceres, trilha de eventos

### Casos de Borda

| ID | Cenário | Comportamento Esperado |
|----|---------|------------------------|
| **EC-001** | `ausente` (valor=null, total=null) | Regras: presença=`ausente`, positividade=`ausente`, consistência=`ausente`; valor_por_parcela=null; analista lista pontos; revisor `inconclusivo` |
| **EC-002** | `divergente` (valor=1000, total=900) | Consistência=`divergente`; analista lista; revisor `inconclusivo` |
| **EC-003** | `violacao` (parcelas=0) | Positividade=`violacao` (parcelas inválido); consistência=`observado` (valor=total); valor_por_parcela=null (divisão por zero evitada); analista lista; revisor `inconclusivo` |
| **EC-004** | Cenário inexistente | API retorna `400` + "Informe somente um ID de cenário sintético válido" |
| **EC-005** | Payload inválido (JSON malformado, chave duplicada, >1KB, campos extras) | API retorna `400` + erro descritivo |
| **EC-006** | Origin não permitido (ex: `http://evil.com`) | API retorna `403` + "Origem não permitida" |
| **EC-007** | Falha de persistência (SQLite indisponível) | API retorna `503` + `DB_ERROR` com auditoria não confirmada |
| **EC-008** | Modo Hermes: gateway indisponível | Adapter lança erro → `service.run` captura → parecer de falha + `revisao_humana: pendente` |
| **EC-009** | Modo Hermes: resposta inválida (schema, tamanho, segredo vazado) | Adapter valida e rejeita → falha propagada → revisão humana |
| **EC-010** | Requisição concorrente múltipla | ThreadingHTTPServer isola threads; cada execução tem UUID próprio; eventos sequenciais por run |

### Fluxos Alternativos

| ID | Fluxo | Descrição |
|----|-------|-----------|
| **AF-001** | Modo Hermes ativo | `CRIVO_MODO=hermes` + chaves + porta → `HermesAdapter` injetado → chamadas HTTP ao gateway local → validação rigorosa de envelope |
| **AF-002** | Analista falha (exceção ou saída inválida) | `service.run` captura → `analista: {status: "falha", texto: "Falha..."}` → revisor não executado (`nao_executado`) → revisão humana |
| **AF-003** | Revisor falha (após analista OK) | `service.run` captura → `revisor: {status: "falha", texto: "Falha..."}` → revisão humana |
| **AF-004** | Consulta de execução inexistente | `GET /api/execucoes/{id}` → `404` + "Não encontrado" |
| **AF-005** | Consulta de eventos de execução inexistente | `GET /api/execucoes/{id}/eventos` → `404` + "Não encontrado" |

### Modos de Falha

| ID | Falha | Mitigação Atual | Gap |
|----|-------|-----------------|-----|
| **FM-001** | SQLite corrompido/indisponível | `503` + erro genérico; sem retry | Sem health check, sem backup |
| **FM-002** | Gateway Hermes cai durante execução | Timeout 15s → falha → revisão humana | Sem circuit breaker, sem fallback |
| **FM-003** | LLM retorna resposta maliciosa (injeta segredo) | Validação `hermes.py:78-80` rejeita | Depende de validação string match |
| **FM-004** | Memória/esgotamento de recursos | Sem limites de conexões/threads | ThreadingHTTPServer unbounded |
| **FM-005** | Binário `cloudflared` / segredo `password` no repo | Documentado no baseline; já público | Não removível do histórico Git |

---

## Ambiguidades

| ID | Ambiguidade | Impacto | Dono | Prazo |
|----|-------------|---------|------|-------|
| **AMB-001** | Revisor simulado nunca retorna `contesta` — apenas `concorda` ou `inconclusivo`. É intencional? | Pode mascarar cenários onde revisor deveria discordar ativamente | Tech Lead | 2026-11-30 |
| **AMB-002** | `valor_por_parcela` é divisão simples sem juros. Requisito futuro: simular juros? | Afeta motor e UI; decisão de produto | PO (Rodrigo) | 2026-12-15 |
| **AMB-003** | Event Sourcing em SQLite: "registro local editável; não há garantia de imutabilidade". Requer imutabilidade criptográfica? | Auditoria regulatória pode exigir | Compliance | 2026-12-15 |
| **AMB-004** | Modo Hermes: gateway não atesta modelo efetivo. Como garantir rastreabilidade de qual modelo rodou? | Governança de IA, compliance | Tech Lead | 2026-12-15 |
| **AMB-005** | Cenários sintéticos fixos vs. entrada livre do usuário. Futuro: permitir payload customizado? | Expansão de escopo, validação extra | PO (Rodrigo) | 2026-12-15 |
| **AMB-006** | Sem autenticação/autorização. Necessário para evolução além de POC? | Segurança, multi-tenancy | Tech Lead | 2026-12-15 |
| **AMB-007** | Métricas de performance (NFR-004, NFR-005) não validadas empiricamente. São targets realistas? | Planejamento de capacidade | Tech Lead | 2026-11-30 |
| **AMB-008** | `demo.py`, `verify.py`, `test_origin_regression.py` — qual o papel de cada um no fluxo de qualidade? | CI/CD, estratégia de testes | QA | 2026-11-30 |

---

## Critérios de Aceite

### REQ-001 a REQ-003 (Motor + Cenários)
- **AC-001**: Dado cenário `completo`, quando `engine.evaluate` executado, então 3 regras com `status: "observado"` e `valor_por_parcela: 100.0`
- **AC-002**: Dado cenário `ausente`, quando `engine.evaluate` executado, então presença=`ausente`, positividade=`ausente`, consistência=`ausente`, `valor_por_parcela: null`
- **AC-003**: Dado cenário `divergente`, quando `engine.evaluate` executado, então consistência=`divergente`
- **AC-004**: Dado cenário `violacao`, quando `engine.evaluate` executado, então positividade=`violacao`, `valor_por_parcela: null`

### REQ-004 a REQ-007 (Analista + Revisor + Human-in-the-loop)
- **AC-005**: Dado regras sem violações, quando `analyst_simulado` executado, então `status: "concluido"` e texto contém "nenhuma inconsistência"
- **AC-006**: Dado regras com violações, quando `analyst_simulado` executado, então texto lista nomes das regras violadas
- **AC-007**: Dado análise concluída sem issues, quando `reviewer_simulado` executado, então `status: "concorda"`
- **AC-008**: Dado análise com issues, quando `reviewer_simulado` executado, então `status: "inconclusivo"`
- **AC-009**: Para qualquer execução completa, quando resultado final gerado, então `revisao_humana: "pendente"` e `estado: "revisao_humana"`
- **AC-010**: Para execução modo simulado, quando resultado final gerado, então `adaptadores.analista: "simulado_local"` e `adaptadores.revisor: "simulado_local"`

### REQ-008 a REQ-009 (Persistência + Auditoria)
- **AC-011**: Dado execução bem-sucedida, quando `service.run` finaliza, então 1 registro em `runs` com UUID único e JSON completo
- **AC-012**: Dado execução bem-sucedida, quando `service.run` finaliza, então 5 eventos em `events` na ordem: `cenario_selecionado`, `regras_executadas`, `analista`, `revisor`, `revisao_humana_necessaria`
- **AC-013**: Dado `GET /api/execucoes/{id}/eventos`, quando executado, então retorna array ordenado por `sequencia` com todos 5 eventos

### REQ-010 a REQ-013 (API REST)
- **AC-014**: Dado `GET /api/cenarios`, quando executado, então retorna array com 4 objetos contendo `id`, `titulo`, `simulacao: true`
- **AC-015**: Dado `POST /api/execucoes` com `{"cenario": "completo"}`, quando executado, então retorna `201` + resultado com `id`, `simulacao: true`, `cenario_id: "completo"`
- **AC-016**: Dado `GET /api/execucoes/{id}` com ID válido, quando executado, então retorna `200` + resultado completo
- **AC-017**: Dado `GET /api/execucoes/{id}` com ID inexistente, quando executado, então retorna `404`
- **AC-018**: Dado `GET /api/execucoes/{id}/eventos` com ID válido, quando executado, então retorna `200` + array de eventos

### REQ-014 (UI)
- **AC-019**: Dado acesso a `http://127.0.0.1:8000/ui`, quando página carrega, então exibe título, aviso de simulação, select com 4 cenários, botão executar
- **AC-020**: Dado cenário selecionado e botão clicado, quando execução completa, então exibe seções: Cenário, Política, Regras, Valor/Parcela, Analista, Revisor, Trilha de eventos

### REQ-015 a REQ-017 (Modos + Falhas)
- **AC-021**: Dado `CRIVO_MODO=simulado` (padrão), quando execução, então analista/revisor = funções locais, sem variáveis de ambiente Hermes
- **AC-022**: Dado `CRIVO_MODO=hermes` + chaves + porta válidas, quando execução, então `HermesAdapter` injetado e chamado
- **AC-023**: Dado falha no analista (exceção), quando `service.run` executa, então `analista.status: "falha"`, `revisor.status: "nao_executado"`, `revisao_humana: "pendente"`

### REQ-018 a REQ-019 (Validação + Segurança)
- **AC-024**: Dado `POST /api/execucoes` com JSON inválido, quando executado, então `400` + erro
- **AC-025**: Dado `POST /api/execucoes` com payload > 1KB, quando executado, então `400` + erro
- **AC-026**: Dado `POST /api/execucoes` com chave duplicada, quando executado, então `400` + erro
- **AC-027**: Dado origin `http://evil.com`, quando `POST /api/execucoes`, então `403` + "Origem não permitida"
- **AC-028**: Dado origin `https://tunnel.trycloudflare.com`, quando `POST /api/execucoes`, então permitido (HTTPS)

### NFR-001 a NFR-020 (Não-Funcionais)
- **AC-029**: Dado mesma entrada repetida 10x, quando `engine.evaluate` executado, então 10 resultados idênticos (determinismo)
- **AC-030**: Dado ambiente Python 3.10+ sem `pip install`, quando `python run_server.py` executado, então servidor inicia sem erro (zero deps)
- **AC-031**: Dado servidor rodando, quando `netstat -an | grep 8000` executado, então bind apenas em `127.0.0.1:8000`
- **AC-032**: Dado execução modo simulado, quando medido, então latência p99 < 100ms
- **AC-033**: Dado 10 requisições concorrentes `POST /api/execucoes`, quando executadas, então todas completam com sucesso (threading)
- **AC-034**: Dado resposta da API, quando headers inspecionados, então `Cache-Control: no-store` e `X-Content-Type-Options: nosniff` presentes
- **AC-035**: Dado modo Hermes com resposta contendo `CRIVO_HERMES_CHAVE_*`, quando `HermesAdapter` valida, então rejeita com erro
- **AC-036**: Dado qualquer resposta da API, quando `simulacao` inspecionado, então `true` e aviso "Não é decisão de crédito" presente

---

## Mapeamento Requisito → Código

| Requisito | Arquivo(s) | Função/Classe | Linhas |
|-----------|------------|---------------|--------|
| REQ-001, REQ-002, REQ-003 | `engine.py` | `evaluate()` | 4-12 |
| REQ-004 | `service.py` | `analyst_simulado()` | 20-22 |
| REQ-005 | `service.py` | `reviewer_simulado()` | 24-26 |
| REQ-006, REQ-007, REQ-008, REQ-009 | `service.py` | `run()` | 31-65 |
| REQ-010, REQ-011, REQ-012, REQ-013, REQ-018, REQ-019 | `server.py` | `Handler.do_GET`, `Handler.do_POST` | 25-58 |
| REQ-014 | `index.html` | (vanilla JS) | 1-27 |
| REQ-015, REQ-016 | `hermes.py` | `configured_adapters()`, `HermesAdapter` | 86-93, 25-83 |
| REQ-017 | `service.py` | `run()` (try/except) | 37-56 |
| NFR-001 | `engine.py`, `service.py` | Funções puras, sem estado | - |
| NFR-002 | Todo projeto | (sem requirements.txt) | - |
| NFR-003 | `server.py` | `ThreadingHTTPServer(('127.0.0.1', port))` | 59 |
| NFR-007 | `service.py` | `event()`, `events()` | 34-60, 71-73 |
| NFR-008 | `service.py` | `CASES` fixo | 9-14 |
| NFR-009, NFR-010, NFR-011 | `server.py` | `Handler.do_POST`, `Handler.send()` | 24, 42-56 |
| NFR-014, NFR-015, NFR-016 | `hermes.py` | `HermesAdapter.__call__()` | 32-81 |
| NFR-017, NFR-018 | `service.py` | `run()` retorno | 59 |
| NFR-019 | `service.py` | `run(analyst=..., reviewer=...)` | 31 |
| NFR-020 | `engine.py` | `POLICY_VERSION` | 1 |

---

## Gaps Identificados (Requisitos vs Implementação)

| Gap ID | Descrição | Severidade | Requisito Afetado | Ação Proposta |
|--------|-----------|------------|-------------------|---------------|
| **GAP-001** | Sem testes automatizados padronizados (pytest/unittest); apenas scripts customizados | Alta | NFR-019 (testabilidade) | Adicionar `pyproject.toml` + `pytest` + test suite |
| **GAP-002** | Sem CI/CD pipeline | Alta | NFR-019, NFR-020 | GitHub Actions: lint, type-check, test |
| **GAP-003** | Sem gestão de dependências (`pyproject.toml`, `requirements.txt`) | Média | NFR-002, NFR-013 | Adicionar `pyproject.toml` com deps opcionais |
| **GAP-004** | Sem linter/formatter/type checker configurado | Média | NFR-019 | Adicionar `ruff`, `mypy`, `black` |
| **GAP-005** | Binário `cloudflared` (40MB) e segredo `password` no repositório Git | Alta (segurança) | NFR-008 | Documentado no baseline; não removível do histórico |
| **GAP-006** | Revisor simulado nunca retorna `contesta` | Baixa | REQ-005, AMB-001 | Clarificar intenção; ajustar se necessário |
| **GAP-007** | Métricas de performance (NFR-004, NFR-005) não validadas | Média | NFR-004, NFR-005, AMB-007 | Benchmark e ajustar targets |
| **GAP-008** | Sem health check / readiness probe | Baixa | NFR-012 | Adicionar endpoint `/health` |
| **GAP-009** | Sem limite de conexões/threads no ThreadingHTTPServer | Baixa | FM-004 | Configurar `ThreadingHTTPServer` com pool |
| **GAP-010** | Event Sourcing não imutável criptograficamente | Média | NFR-007, AMB-003 | Avaliar assinatura/hashing de eventos |
| **GAP-011** | Modo Hermes: sem circuit breaker, retry, observabilidade de latência | Média | NFR-014, FM-002 | Adicionar resiliência no adapter |
| **GAP-012** | Sem documentação de API (OpenAPI/Swagger) | Baixa | REQ-010 a REQ-013 | Gerar spec OpenAPI |

---

## Próximos Passos

1. **Aprovação deste Requirements Analysis** — Sign-off PO (Rodrigo) + Tech Lead + QA
2. **Executar domain-design (stage 1.3)** — Modelar domínio, entidades, value objects, agregados
3. **Executar contract-design (stage 1.4)** — Definir contratos de API (OpenAPI), schemas de eventos
4. **Executar delivery-planning (stage 1.5)** — Priorizar gaps, planejar sprints, definir Done
5. **Executar approval-handoff (stage 1.6)** — Gate 5: Inception → Construction

---

## Tradeoffs Documentados

| Decisão | Tradeoff | Racional |
|---------|----------|----------|
| Python stdlib only | Sem framework web, validação manual | POC simples, zero deps, portável |
| SQLite embarcado | Sem servidor DB, single-file | Demo local, sem infra |
| Event Sourcing em SQLite | Mais storage, queries complexas | Auditoria completa, rastreabilidade |
| Human-in-the-loop sempre | Latência, não escalável | Compliance, segurança, regulatório |
| Dois modos via DI | Duplicação lógica parecer | Flexibilidade, out-of-the-box + opt-in LLM |
| Revisor nunca `contesta` | Menos cobertura de cenário | Simplificação da POC; pode evoluir |

---

*Requirements Analysis completo. Pronto para Gate 5 (Inception → Construction) após sign-off dos stakeholders.*