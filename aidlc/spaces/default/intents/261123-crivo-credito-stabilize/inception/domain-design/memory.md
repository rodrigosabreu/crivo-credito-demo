# Domain Design — Memory

> **Stage**: domain-design | **Phase**: inception | **Intent**: 261123-crivo-credito-stabilize
> **Date**: 2026-11-23 | **Agent**: Polaris (PM)

---

## Visão Geral do Domínio

O domínio **Crivo Crédito Demo** modela um processo de **simulação de análise de crédito exclusivamente sintética**. Não concede, nega ou recomenda crédito. O domínio é centrado na execução determinística de um motor de regras versionado (`politica: demonstrativa-1.0`), orquestração de pareceres (analista + revisor simulados ou via gateway Hermes), persistência com Event Sourcing para auditoria completa, e exigência obrigatória de human-in-the-loop.

### Princípios de Domínio

| Princípio | Descrição |
|-----------|-----------|
| **Determinismo** | Mesma entrada → mesmo resultado (motor, analista, revisor simulados) |
| **Imutabilidade de Política** | `politica: demonstrativa-1.0` é imutável no código; alteração = nova versão |
| **Auditoria Total** | Event Sourcing: todo passo rastreado com timestamp UTC, sequência, detalhes JSON |
| **Human-in-the-loop Obrigatório** | Estado final sempre `revisao_humana: pendente`; sistema não decide |
| **Rastreabilidade de Origem** | Identificar se analista/revisor vieram de `simulado_local` ou `adaptador_hermes_..._modelo_nao_verificado` |
| **Zero Dados Reais** | Catálogo sintético fixo; sem CPF, documentos, PII |
| **Dois Modos via DI** | Simulado (padrão, zero deps) / Hermes (opt-in, gateway local) |

---

## Modelo de Domínio (DDD)

### 1. Bounded Contexts

O domínio é **único e coeso** — não há múltiplos bounded contexts. Todo o sistema opera dentro do contexto **"Simulação de Análise de Crédito Sintética"**.

**Justificativa:**
- Escopo pequeno e focado (POC)
- Todos os conceitos estão intimamente ligados (cenário → regras → pareceres → auditoria → revisão humana)
- Não há subdomínios independentes com linguagens ubíquas distintas
- Evolução futura pode extrair bounded contexts (ex: `Policy Management`, `Audit Trail`, `LLM Gateway`) se o escopo crescer

---

### 2. Agregados (Aggregates)

#### Aggregate Root: **ExecucaoSimulacao** (Execution)

| Atributo | Tipo | Descrição |
|----------|------|-----------|
| `id` | UUID (hex) | Identificador único da execução |
| `simulacao` | boolean | Sempre `true` (marcador de simulação sintética) |
| `aviso` | string | "Simulação exclusivamente sintética. Não é decisão de crédito." |
| `cenario_id` | string | ID do cenário selecionado (`completo`, `ausente`, `divergente`, `violacao`) |
| `cenario` | Cenario (Value Object) | Snapshot completo do cenário no momento da execução |
| `politica` | Politica (Value Object) | Versão e descrição da política aplicada |
| `motor` | MotorResultado (Value Object) | Resultado do motor de regras (3 regras + valor_por_parcela) |
| `analista` | Parecer (Entity) | Parecer do analista (simulado ou Hermes) |
| `revisor` | Parecer (Entity) | Parecer do revisor (simulado ou Hermes) |
| `adaptadores` | AdaptadoresOrigem (Value Object) | Origem de cada adaptador (simulado_local / adaptador_hermes_...) |
| `estado` | string | Sempre `revisao_humana` |
| `revisao_humana` | string | Sempre `pendente` |

**Invariantes do Agregado:**
1. `simulacao` **sempre** `true`
2. `estado` **sempre** `revisao_humana`
3. `revisao_humana` **sempre** `pendente`
4. `cenario_id` deve existir em `CASES` (catálogo fixo)
5. `politica.versao` deve ser `demonstrativa-1.0` (imutável)
6. `analista.status` ∈ {`concluido`, `falha`}
7. `revisor.status` ∈ {`concorda`, `contesta`, `inconclusivo`, `falha`, `nao_executado`}
8. Se `analista.status == falha`, então `revisor.status == nao_executado`
9. `adaptadores.analista` e `adaptadores.revisor` não vazios

**Métodos de Fábrica:**
- `ExecucaoSimulacao.criar(cenario_id, motor_resultado, analista, revisor, adaptadores)` — valida invariantes e cria instância

---

### 3. Entidades (Entities)

#### **Parecer** (Analyst/Reviewer Opinion)

| Atributo | Tipo | Descrição |
|----------|------|-----------|
| `status` | string | Estado do parecer (ver invariantes acima) |
| `texto` | string | Texto explicativo com evidências e limitações (1-2000 chars) |

**Identidade:** Não tem identidade própria — faz parte do agregado `ExecucaoSimulacao`. Dois pareceres com mesmo conteúdo em execuções diferentes são distintos.

**Validação (`service._valid`):**
- Deve ser `dict` com chaves exatamente `{'status', 'texto'}`
- `status` deve estar no conjunto permitido por role
- `texto` deve ser string não-vazia ≤ 2000 chars

---

### 4. Value Objects

#### **Cenario** (Scenario)

| Atributo | Tipo | Descrição |
|----------|------|-----------|
| `titulo` | string | Título legível (ex: "Completo e consistente") |
| `valor` | int \| null | Valor do crédito (centavos ou unidade monetária) |
| `parcelas` | int | Número de parcelas |
| `total_declarado` | int \| null | Total declarado pelo solicitante |

**Catálogo Fixo (`service.CASES`):**
```python
'completo':   {'titulo': 'Completo e consistente', 'valor': 1000, 'parcelas': 10, 'total_declarado': 1000}
'ausente':    {'titulo': 'Dados ausentes', 'valor': None, 'parcelas': 10, 'total_declarado': None}
'divergente': {'titulo': 'Total divergente', 'valor': 1000, 'parcelas': 10, 'total_declarado': 900}
'violacao':   {'titulo': 'Quantidade de parcelas inválida', 'valor': 1000, 'parcelas': 0, 'total_declarado': 1000}
```

**Imutabilidade:** Instâncias são criadas uma vez no carregamento do módulo; nunca modificadas.

#### **Politica** (Policy Version)

| Atributo | Tipo | Descrição |
|----------|------|-----------|
| `versao` | string | `demonstrativa-1.0` (constante `engine.POLICY_VERSION`) |
| `descricao` | string | Descrição legível da política |

**Imutabilidade:** Constante no código; alteração requer nova versão (ex: `demonstrativa-1.1`) e deploy.

#### **RegraAvaliacao** (Rule Evaluation)

| Atributo | Tipo | Descrição |
|----------|------|-----------|
| `regra` | string | Nome da regra (ex: "Presença dos campos") |
| `status` | string | `observado` \| `ausente` \| `violacao` \| `divergente` |
| `evidencia` | string | Evidência textual da avaliação |

**Regras do Motor (`engine.evaluate`):**
1. **Presença dos campos** — Verifica se `valor`, `parcelas`, `total_declarado` não são `null`
2. **Valores inteiros positivos** — Verifica se campos presentes são `int > 0`
3. **Total declarado igual ao valor** — Verifica `valor == total_declarado`

#### **MotorResultado** (Engine Result)

| Atributo | Tipo | Descrição |
|----------|------|-----------|
| `politica` | string | Versão da política (`demonstrativa-1.0`) |
| `regras` | list[RegraAvaliacao] | Lista das 3 regras avaliadas |
| `valor_por_parcela` | float \| null | `round(valor / parcelas, 2)` se válido; `null` caso contrário |
| `nota_calculo` | string | "Divisão demonstrativa sem juros; não é oferta." |

#### **AdaptadoresOrigem** (Adapter Origins)

| Atributo | Tipo | Descrição |
|----------|------|-----------|
| `analista` | string | `simulado_local` \| `adaptador_hermes_local_perfil_solicitado_crivo_analista_modelo_nao_verificado` \| `adaptador_injetado_origem_nao_verificada` |
| `revisor` | string | `simulado_local` \| `adaptador_hermes_local_perfil_solicitado_crivo_revisor_modelo_nao_verificado` \| `adaptador_injetado_origem_nao_verificada` |

---

### 5. Domain Events (Eventos de Domínio)

Registrados via **Event Sourcing** na tabela `events`. Cada execução gera 5 eventos em sequência fixa:

| Sequência | Tipo | Detalhes (JSON) | Descrição |
|-----------|------|-----------------|-----------|
| 1 | `cenario_selecionado` | `{'cenario': 'completo', 'fonte': 'catálogo sintético local'}` | Cenário escolhido pelo usuário |
| 2 | `regras_executadas` | `MotorResultado` completo | Resultado do motor determinístico |
| 3 | `analista` | `{'origem': 'simulado_local', 'resultado': Parecer}` | Parecer do analista |
| 4 | `revisor` | `{'origem': 'simulado_local', 'resultado': Parecer}` | Parecer do revisor |
| 5 | `revisao_humana_necessaria` | `{'estado': 'revisao_humana'}` | Marca obrigatoriedade de revisão humana |

**Propriedades dos Eventos:**
- `seq` — Auto-increment (PK)
- `run_id` — FK para `runs.id`
- `timestamp` — UTC ISO 8601 (`datetime.now(timezone.utc).isoformat()`)
- `tipo` — Um dos 5 tipos acima
- `detalhes` — JSON serializado (`ensure_ascii=False`)

**Imutabilidade:** Eventos **nunca** modificados após inserção. Append-only.

---

### 6. Serviços de Domínio (Domain Services)

#### **MotorRegras** (`engine.evaluate`)

**Responsabilidade:** Avaliar as 3 regras determinísticas sobre um cenário.

**Entrada:** `Cenario` (dict com `valor`, `parcelas`, `total_declarado`)

**Saída:** `MotorResultado`

**Regras de Negócio:**
```
R1 - Presença:     Se qualquer campo (valor, parcelas, total_declarado) é null → status='ausente'
                   Senão → status='observado'

R2 - Positividade: Se R1='ausente' → status='ausente'
                   Senão se qualquer campo presente não é int > 0 → status='violacao'
                   Senão → status='observado'

R3 - Consistência: Se valor ou total_declarado é null → status='ausente'
                   Senão se valor != total_declarado → status='divergente'
                   Senão → status='observado'

Valor por Parcela: Se valor e parcelas são int > 0 → round(valor / parcelas, 2)
                   Senão → null
```

**Determinismo:** Função pura, sem estado, sem I/O, sem tempo. Mesma entrada → mesma saída.

#### **AnalistaSimulado** (`service.analyst_simulado`)

**Responsabilidade:** Gerar parecer conclusivo baseado nas regras.

**Entrada:** `Cenario`, `MotorResultado`

**Saída:** `Parecer` com `status='concluido'`

**Lógica:**
- Coleta nomes das regras com `status != 'observado'`
- Se lista vazia: texto = "Simulação determinística: nenhuma inconsistência nas regras demonstrativas; isso não é decisão de crédito."
- Senão: texto = "Simulação determinística: pontos para revisão: " + lista de regras

#### **RevisorSimulado** (`service.reviewer_simulado`)

**Responsabilidade:** Gerar veredito acompanhando o analista.

**Entrada:** `Cenario`, `MotorResultado`, `Parecer` (analista)

**Saída:** `Parecer` com `status ∈ {'concorda', 'inconclusivo'}`

**Lógica:**
- Coleta nomes das regras com `status != 'observado'`
- Se lista vazia: `status='concorda'`, texto = "Simulação: o resumo acompanha as regras demonstrativas; concordância não prova correção."
- Senão: `status='inconclusivo'`, texto = "Simulação: há pontos que exigem revisão humana: " + lista de regras

**Nota:** Implementação atual **nunca** retorna `contesta` (ver AMB-001).

#### **OrquestradorExecucao** (`service.run`)

**Responsabilidade:** Coordenar fluxo completo: motor → analista → revisor → persistência → eventos.

**Entrada:** `db_path`, `scenario_id`, `analyst` (opcional, default=simulado), `reviewer` (opcional, default=simulado)

**Fluxo:**
1. Valida `scenario_id` ∈ `CASES`
2. Executa `engine.evaluate(case)` → `rules`
3. Emite evento `cenario_selecionado`
4. Emite evento `regras_executadas`
5. Chama `analyst(case, rules)` com validação `_valid`; em caso de falha → parecer de falha
6. Emite evento `analista` com origem
7. Se analista falhou: revisor = `nao_executado`
8. Senão: chama `reviewer(case, rules, analysis)` com validação; em caso de falha → parecer de falha
9. Emite evento `revisor` com origem
10. Constrói `ExecucaoSimulacao` (aggregate root)
11. Emite evento `revisao_humana_necessaria`
12. Persiste em `runs` + `events` (transação única)
13. Retorna `ExecucaoSimulacao`

**Injeção de Dependência:** `analyst` e `reviewer` são parâmetros — permite testes e modo Hermes.

---

## Mapeamento para Implementação Atual

| Conceito de Domínio | Implementação Atual | Arquivo |
|---------------------|---------------------|---------|
| `Cenario` | `dict` em `CASES` | `service.py:9-14` |
| `Politica` | `engine.POLICY_VERSION`, `engine.POLICY` | `engine.py:1-2` |
| `RegraAvaliacao` | `dict` com `regra`, `status`, `evidencia` | `engine.py:7-11` |
| `MotorResultado` | `dict` retorno de `engine.evaluate` | `engine.py:4-12` |
| `Parecer` | `dict` com `status`, `texto` | `service.py:20-26` |
| `AdaptadoresOrigem` | `dict` retorno de `origin()` | `service.py:43-46` |
| `ExecucaoSimulacao` | `dict` retorno de `service.run` | `service.py:58-60` |
| Domain Events | Tuplas `(kind, details)` → tabela `events` | `service.py:34-35, 61-64` |
| `MotorRegras` | `engine.evaluate()` | `engine.py:4-12` |
| `AnalistaSimulado` | `service.analyst_simulado()` | `service.py:20-22` |
| `RevisorSimulado` | `service.reviewer_simulado()` | `service.py:24-26` |
| `OrquestradorExecucao` | `service.run()` | `service.py:31-65` |
| Persistência Runs | Tabela `runs` (id, result JSON) | `service.py:18, 61-64` |
| Persistência Events | Tabela `events` (seq, run_id, timestamp, tipo, detalhes) | `service.py:18, 61-64` |
| API REST | `server.py` Handler | `server.py` |
| UI | `index.html` vanilla JS | `index.html` |
| Hermes Adapter | `hermes.HermesAdapter` | `hermes.py:25-83` |
| Configuração Modos | `hermes.configured_adapters()` | `hermes.py:86-93` |

---

## Regras de Negócio Documentadas

### RN-001: Catálogo de Cenários Fixos
**Descrição:** Sistema oferece exatamente 4 cenários sintéticos imutáveis.
**Implementação:** `service.CASES` (dict constante)
**Validação:** `service.run` levanta `ValueError` se cenário não existe

### RN-002: Motor de Regras Versionado Imutável
**Descrição:** Política `demonstrativa-1.0` com 3 regras fixas; alteração = nova versão no código.
**Implementação:** `engine.POLICY_VERSION`, `engine.evaluate()`
**Validação:** `engine.POLICY_VERSION` constante; `engine.evaluate` função pura

### RN-003: Cálculo de Valor por Parcela (Demonstrativo)
**Descrição:** Divisão simples `valor / parcelas` sem juros; `null` se inválido.
**Implementação:** `engine.py:12`
**Aviso:** Incluído em todo resultado: "Divisão demonstrativa sem juros; não é oferta."

### RN-004: Analista Conclusivo
**Descrição:** Sempre retorna `status='concluido'` listando inconsistências ou confirmando ausência.
**Implementação:** `service.analyst_simulado()`

### RN-005: Revisor Acompanha (Nunca Contesta Atualmente)
**Descrição:** Retorna `concorda` (sem issues) ou `inconclusivo` (com issues). `contesta` não usado.
**Implementação:** `service.reviewer_simulado()`
**Gap:** AMB-001 — clarificar se intencional

### RN-006: Human-in-the-loop Obrigatório
**Descrição:** Estado final **sempre** `revisao_humana: pendente`; sistema não decide.
**Implementação:** `service.run` linha 59: `'estado': 'revisao_humana', 'revisao_humana': 'pendente'`

### RN-007: Rastreabilidade de Origem
**Descrição:** Identificar origem de cada adaptador (simulado vs Hermes).
**Implementação:** `service.origin()` → `adaptadores` no resultado

### RN-008: Persistência Atômica (Runs + Events)
**Descrição:** Execução completa persistida em transação única: 1 run + 5 events.
**Implementação:** `service.run` linhas 61-64 (mesmo `with closing...`)

### RN-009: Event Sourcing para Auditoria
**Descrição:** Trilha imutável ordenada: cenario → regras → analista → revisor → revisao_humana.
**Implementação:** Tabela `events` com `seq` auto-increment, consulta ordenada por `seq`

### RN-010: Dois Modos via Injeção de Dependência
**Descrição:** Modo simulado (padrão) e modo Hermes (opt-in) via parâmetros `analyst`/`reviewer`.
**Implementação:** `service.run(analyst=..., reviewer=...)`, `hermes.configured_adapters()`

### RN-011: Falha de Adaptador → Revisão Humana
**Descrição:** Erro em analista/revisor (simulado ou Hermes) → parecer de falha + revisão humana.
**Implementação:** `service.run` try/except linhas 37-56

### RN-012: Validação de Entrada API
**Descrição:** Rejeitar payload inválido (não JSON, chaves duplicadas, >1KB, campos inesperados).
**Implementação:** `server.py:9-15` (unique_keys), `server.py:50-56`

### RN-013: Origin Validation (CSRF Básico)
**Descrição:** Permitir apenas localhost/127.0.0.1 e origens HTTPS (túneis).
**Implementação:** `server.py:42-49`

### RN-014: Headers de Segurança
**Descrição:** `Cache-Control: no-store`, `X-Content-Type-Options: nosniff` em todas respostas.
**Implementação:** `server.py:24`

---

## Análise de Modelo Atual vs. Rich Domain Model

### Estado Atual: **Modelo Anêmico**
- Entidades/Value Objects representados como `dict`s planos
- Lógica de negócio em funções puras (`engine.py`, `service.py`)
- Nenhum encapsulamento de invariantes no nível de objeto
- Validação dispersa (`_valid` em service, validações em server, hermes)

### Evolução Potencial: **Rich Domain Model**
| Conceito | Atual (Anêmico) | Proposto (Rich) |
|----------|-----------------|-----------------|
| `Cenario` | `dict` | `@dataclass(frozen=True)` com validação no `__post_init__` |
| `Politica` | Constantes módulo | `class Politica` imutável com versionamento semântico |
| `RegraAvaliacao` | `dict` | `@dataclass(frozen=True)` |
| `MotorResultado` | `dict` | `class MotorResultado` com métodos de consulta |
| `Parecer` | `dict` | `class Parecer` com factory methods por status |
| `ExecucaoSimulacao` | `dict` | Aggregate Root com invariantes encapsulados |
| `Analista/Revisor` | Funções | Strategy Pattern com interface `Port` |
| Eventos | Tuplas + SQL | Domain Events como classes, Event Store abstraction |

**Tradeoff:** Modelo anêmico atual é adequado para POC (simples, zero deps, determinístico). Rich model adiciona complexidade (validação, boilerplate) mas melhora:
- Expressividade do domínio
- Encapsulamento de invariantes
- Testabilidade isolada
- Extensibilidade (novas regras, políticas, adaptadores)

**Recomendação:** Manter modelo anêmico para POC. Evoluir para rich model na fase **Construction** se:
- Novas políticas de crédito forem adicionadas
- Regras de negócio tornarem-se complexas
- Necessidade de múltiplos bounded contexts
- Time crescer e precisar de contratos mais explícitos

---

## Políticas de Crédito Versionadas — Evolução Futura

### Modelo Atual
- Versão hardcoded: `demonstrativa-1.0`
- 3 regras fixas no código
- Alteração = novo deploy

### Modelo Futuro Proposto
```
Politica (Aggregate Root)
├── versao: "demonstrativa-1.0" (semver)
├── descricao: string
├── regras: List[RegraConfig]  # Configurável, não hardcoded
├── vigencia_inicio: datetime
├── vigencia_fim: datetime | null
└── status: ATIVA | DEPRECADA | ARQUIVADA
```

**Estratégia de Migração:**
1. Extrair regras para configuração (JSON/YAML/DB)
2. Versionamento semântico (major = breaking, minor = nova regra, patch = ajuste)
3. Motor avalia regras da política ativa na data da execução
4. Histórico de políticas para auditoria retroativa

---

## Event Sourcing como Source of Truth — CQRS Futuro

### Estado Atual
- Event Store = tabela `events` SQLite
- Read Model = tabela `runs` (JSON completo) + consulta `events`
- Single model para read/write

### CQRS Futuro (se necessário)
| Comando (Write) | Consulta (Read) |
|-----------------|-----------------|
| `ExecutarSimulacao` | `ObterExecucaoPorId` |
| `RegistrarParecerAnalista` | `ListarExecucoesPorCenario` |
| `RegistrarParecerRevisor` | `ObterTrilhaEventos` |
| `MarcarRevisaoHumana` | `BuscarExecucoesPorPeriodo` |
|  | `DashboardMetricas` (latência, throughput, distribuição status) |

**Quando adotar:** Se houver necessidade de:
- Múltiplas visões de leitura otimizadas
- Escalabilidade de leitura independente de escrita
- Integração com sistemas externos (BI, relatórios)
- Replay de eventos para reconstruir estado

---

## Integração Hermes como External Service — Anti-Corruption Layer

### Estado Atual
- `HermesAdapter` implementa `__call__` compatível com assinatura `(case, rules, analysis?)`
- Validação rigorosa de envelope Hermes + resposta
- Injeção direta em `service.run`

### Anti-Corruption Layer (ACL) Explícito
```
┌─────────────────────────────────────────────────────────────┐
│                      DOMÍNIO CRI VO                         │
│  service.run(analyst: AnalystPort, reviewer: ReviewerPort) │
└──────────────────────────┬──────────────────────────────────┘
                           │ Depende de abstração (Port)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    ANTI-CORRUPTION LAYER                    │
│  SimulatedAnalystAdapter  ── implements ──►  AnalystPort   │
│  SimulatedReviewerAdapter ── implements ──►  ReviewerPort  │
│  HermesAnalystAdapter     ── implements ──►  AnalystPort   │
│  HermesReviewerAdapter    ── implements ──►  ReviewerPort  │
└──────────────────────────┬──────────────────────────────────┘
                           │ Isola domínio de detalhes Hermes
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   EXTERNAL: HERMES GATEWAY                  │
│  HTTP POST /p/crivo-analista/v1/chat/completions           │
│  HTTP POST /p/crivo-revisor/v1/chat/completions            │
└─────────────────────────────────────────────────────────────┘
```

**Benefícios do ACL:**
- Domínio não conhece `HermesAdapter`, `http.client`, envelopes, timeouts
- Testes usam `SimulatedAnalystAdapter` (já existe como `analyst_simulado`)
- Troca de gateway LLM não afeta domínio
- Validação de contrato (Port) em tempo de execução

**Implementação Mínima (Python stdlib):**
```python
# ports.py
from abc import ABC, abstractmethod
from typing import Protocol

class AnalystPort(Protocol):
    def __call__(self, case: dict, rules: dict) -> dict: ...

class ReviewerPort(Protocol):
    def __call__(self, case: dict, rules: dict, analysis: dict) -> dict: ...

# adapters/simulated.py
def analyst_simulado(case, rules) -> dict: ...
def reviewer_simulado(case, rules, analysis) -> dict: ...

# adapters/hermes.py
class HermesAnalystAdapter:
    def __init__(self, port, key): ...
    def __call__(self, case, rules) -> dict: ...  # validação + HTTP

class HermesReviewerAdapter:
    def __init__(self, port, key): ...
    def __call__(self, case, rules, analysis) -> dict: ...
```

**Recomendação:** Implementar ACL na fase **Construction** (functional-design → code-generation) para preparar evolução.

---

## Identificação de Gaps de Domínio (do Requirements Analysis)

| Gap ID | Descrição | Impacto no Domínio | Ação |
|--------|-----------|-------------------|------|
| **GAP-006** | Revisor nunca retorna `contesta` | `Parecer.status` domain value incompleto | Clarificar requisito; ajustar `reviewer_simulado` se necessário |
| **AMB-001** | Revisor nunca `contesta` — intencional? | Modelo de domínio permite `contesta` mas não usado | Decisão de produto (PO) |
| **AMB-002** | Juros no cálculo de parcela | `MotorResultado.valor_por_parcela` fórmula fixa | Decisão de produto; se sim → nova regra ou parâmetro |
| **AMB-003** | Imutabilidade criptográfica eventos | `Event` não garante integridade | Avaliar assinatura/hashing se compliance exigir |
| **AMB-004** | Rastreabilidade modelo Hermes | `AdaptadoresOrigem` diz `modelo_nao_verificado` | Governança de IA; pode requerer atestação do gateway |
| **AMB-005** | Cenários fixos vs entrada livre | `Cenario` value object fechado | Decisão de produto; se entrada livre → validação extra |
| **AMB-006** | Autenticação/autorização | Aggregate root não tem `usuario_id` | Para além de POC: adicionar identidade, multi-tenancy |

---

## Tradeoffs de Design de Domínio

| Decisão | Tradeoff | Racional |
|---------|----------|----------|
| **Modelo anêmico (dicts)** | Menos encapsulamento, validação dispersa | POC simples, zero deps, determinístico, fácil de inspecionar/debuggar |
| **Catálogo fixo imutável** | Não permite entrada de usuário | Segurança (zero dados reais), determinismo, simplicidade |
| **Event Sourcing em SQLite** | Mais storage, queries complexas | Auditoria completa, rastreabilidade, compliance |
| **Human-in-the-loop sempre** | Latência, não escalável | Compliance, segurança, regulatório (não decisão de crédito) |
| **Dois modos via DI** | Duplicação lógica parecer (simulado vs Hermes) | Flexibilidade, out-of-the-box + opt-in LLM, testabilidade |
| **Revisor nunca `contesta`** | Menos cobertura de cenário | Simplificação da POC; pode evoluir se produto demandar |
| **Política hardcoded** | Deploy para alterar regras | POC scope; versão no código = rastreabilidade implícita |
| **Sem ACL explícito** | Domínio acoplado a detalhes Hermes | POC escopo; ACL adiciona abstração que pode ser YAGNI |

---

## Perguntas Abertas (do Requirements Analysis + Novas)

| ID | Pergunta | Impacto | Dono | Prazo |
|----|----------|---------|------|-------|
| **DOM-001** | Evoluir para Rich Domain Model na Construction? | Arquitetura, testabilidade, manutenibilidade | Tech Lead | 2026-12-15 |
| **DOM-002** | Extrair políticas para configuração versionada (não hardcoded)? | Extensibilidade, auditoria retroativa | PO + Tech Lead | 2026-12-15 |
| **DOM-003** | Adotar CQRS (separar read/write models)? | Escalabilidade, múltiplas visões | Tech Lead | 2026-12-31 |
| **DOM-004** | Implementar Anti-Corruption Layer explícito para Hermes? | Isolamento de domínio, testabilidade, evolução gateway | Tech Lead | 2026-12-15 |
| **DOM-005** | Adicionar assinatura criptográfica/hashing aos eventos? | Imutabilidade auditável, compliance | Compliance | 2026-12-15 |
| **DOM-006** | Permitir cenários customizados (entrada livre) vs catálogo fixo? | Escopo, validação, segurança | PO (Rodrigo) | 2026-12-15 |
| **DOM-007** | Adicionar identidade de usuário (auth) para multi-tenancy? | Segurança, auditoria, evolução além de POC | Tech Lead | 2026-12-31 |
| **DOM-008** | `reviewer_simulado` deve retornar `contesta` em algum caso? | Completude do modelo de domínio | PO + Tech Lead | 2026-11-30 |

---

## Próximos Passos

1. **Aprovação deste Domain Design** — Sign-off PO (Rodrigo) + Tech Lead + QA
2. **Executar contract-design (stage 1.4)** — Definir contratos de API (OpenAPI), schemas de eventos, Ports (AnalystPort, ReviewerPort)
3. **Executar delivery-planning (stage 1.5)** — Priorizar gaps, planejar sprints, definir Done
4. **Executar approval-handoff (stage 1.6)** — Gate 5: Inception → Construction

---

## Referências

- Requirements Analysis: `aidlc/spaces/default/intents/261123-crivo-credito-stabilize/inception/requirements-analysis/memory.md`
- Código fonte: `crivo/engine.py`, `crivo/service.py`, `crivo/server.py`, `crivo/hermes.py`, `crivo/index.html`
- ADRs Baseline: `docs/adr/ADR-001` a `ADR-007`
- ADRs Governança: `docs/adr/ADR-008` a `ADR-012`

---

*Domain Design completo. Pronto para Gate 5 (Inception → Construction) após sign-off dos stakeholders e execução de contract-design, delivery-planning, approval-handoff.*