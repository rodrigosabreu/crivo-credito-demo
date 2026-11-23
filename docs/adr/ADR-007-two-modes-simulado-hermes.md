# ADR-007: Dois modos de execução: simulado (padrão) e hermes (opt-in)

## Status
Implemented

## Contexto
A aplicação deve funcionar imediatamente sem dependências externas (modo simulado) e opcionalmente integrar com gateway Hermes para analista/revisor baseados em LLM (modo hermes).

## Decisão
- **Modo simulado (padrão)**: `CRIVO_MODO` não definido ou `simulado`
  - Analista: `analista_simulado()` — função Python local
  - Revisor: `revisor_simulado()` — função Python local
  - Zero dependências externas
  - Execução imediata: `python run_server.py`
  
- **Modo hermes (opt-in)**: `CRIVO_MODO=hermes` + variáveis de ambiente
  - `CRIVO_HERMES_CHAVE_ANALISTA` — chave para intent `crivo-analista`
  - `CRIVO_HERMES_CHAVE_REVISOR` — chave para intent `crivo-revisor`
  - `CRIVO_HERMES_PORTA` — porta do gateway (padrão 8888)
  - Analista: `HermesAdapter(intent="crivo-analista")` — HTTP → Gateway
  - Revisor: `HermesAdapter(intent="crivo-revisor")` — HTTP → Gateway
  - Requer gateway Hermes rodando em loopback
  - **Sem fallback automático** — falha no Hermes = parecer falha + revisão humana

- Injeção de dependência via `Service(analista=..., revisor=...)`
- Factory em `server.py` cria adapters baseados em `CRIVO_MODO`

## Alternativas Consideradas
| Alternativa | Prós | Contras | Decisão |
|-------------|------|---------|---------|
| 1. Apenas modo simulado | Simples, sempre funciona | Sem extensibilidade LLM | Rejeitada |
| 2. Apenas modo Hermes | LLM nativo | Requer infra, não roda standalone | Rejeitada |
| 3. Dois modos com DI + opt-in | Flexível, roda standalone, extensível | Mais complexidade | **Aceita** |
| 4. Fallback automático simulado se Hermes falha | Resiliente | Mascara falhas, viola HITL | Rejeitada |

## Consequências
### Positivas
- Standalone por padrão: `python run_server.py` funciona sempre
- Extensível: LLM via Hermes opt-in
- Explícito: sem fallback silencioso — falha visível
- Testável: modo simulado = unit tests, modo hermes = integration tests

### Negativas
- Duplicação de lógica adapter (simulado vs Hermes)
- Configuração manual para modo Hermes

### Riscos
- Gateway Hermes indisponível → execução falha (intencional)
- Chaves expostas em env vars (mitigado: loopback only, POC)

### Mitigações
- Documentação clara: variáveis necessárias para modo Hermes
- Testes: modo simulado para CI, modo hermes para integration tests manuais

## Impacto de Compliance
- [ ] Regulatório financeiro
- [ ] LGPD
- [ ] SOX
- [ ] PCI-DSS
- [ ] ANBIMA
- [ ] CMN 4.658
- [x] Outro: Extensibilidade controlada, sem fallback silencioso

## Impacto AI-DLC
- **Eval gates afetados**: Nenhum (decisão pré-existente)
- **Pipeline changes**: N/A
- **Observabilidade needs**: Adapter type registrado em eventos (`simulado_local` vs `adaptador_hermes_...`)
- **Model routing changes**: Adapter pattern permite routing futuro
- **Cost impact**: Zero (simulado), custo LLM (hermes opt-in)

## Implementation Notes
- `service.py`: `Service.__init__(analista, revisor)` — DI via construtor
- `server.py`: `criar_adapters()` — factory baseada em `os.getenv("CRIVO_MODO")`
- `hermes.py`: `HermesAdapter` — HTTP POST para gateway, timeout 30s
- Variáveis: `CRIVO_MODO`, `CRIVO_HERMES_CHAVE_ANALISTA`, `CRIVO_HERMES_CHAVE_REVISOR`, `CRIVO_HERMES_PORTA`

## References
- `crivo/service.py` — DI e Service class
- `crivo/server.py` — factory `criar_adapters()`
- `crivo/hermes.py` — `HermesAdapter` class

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