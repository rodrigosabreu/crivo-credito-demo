# ADR-002: Arquitetura em camadas: Engine → Service → Server → Adapters

## Status
Implemented

## Contexto
A aplicação precisa separar claramente: regras de negócio determinísticas (engine), orquestração de casos e persistência (service), interface HTTP (server), e adaptadores para analista/revisor (simulado vs Hermes).

## Decisão
Arquitetura em 4 camadas com injeção de dependência:
1. **Engine** (`engine.py`): Motor determinístico puro — regras versionadas, cálculo, sem I/O
2. **Service** (`service.py`): Orquestração — casos, analista, revisor, persistência, adapters injetáveis
3. **Server** (`server.py`): HTTP API — endpoints, validação origem, CORS, CSRF
4. **Adapters** (`hermes.py` + funções simuladas): Analista/revisor — `analista_simulado`, `revisor_simulado`, `HermesAdapter`

Injeção de dependência via parâmetros construtor/parâmetros de função — sem container DI.

## Alternativas Consideradas
| Alternativa | Prós | Contras | Decisão |
|-------------|------|---------|---------|
| 1. Monolito único | Simples | Acoplamento forte, difícil testar | Rejeitada |
| 2. 3 camadas (Engine+Service, Server, Adapters) | Menos arquivos | Service mistura orquestração + persistência | Rejeitada |
| 3. 4 camadas com DI | Separação clara, testável, extensível | Mais arquivos | **Aceita** |

## Consequências
### Positivas
- Engine testável isoladamente (funções puras)
- Service trocável (persistência, adapters)
- Dois modos execução via DI (simulado/hermes)
- Segurança: Server valida origem antes de chamar Service

### Negativas
- Mais arquivos para projeto pequeno
- Overhead de passagem de adapters

### Riscos
- Vazamento de responsabilidades entre camadas

### Mitigações
- Convenção: Engine = zero I/O, Service = orquestração apenas
- Code reviews para enforcar separação

## Impacto de Compliance
- [x] Outro: Separação suporta auditoria (Event Sourcing no Service)

## Impacto AI-DLC
- **Eval gates afetados**: Nenhum (decisão pré-existente)
- **Pipeline changes**: N/A
- **Observabilidade needs**: Event Sourcing no Service
- **Model routing changes**: Adapter pattern permite Hermes opt-in
- **Cost impact**: Zero

## Implementation Notes
- `engine.py`: `calcular()`, `executar_regras()` — funções puras
- `service.py`: `Caso`, `Analista`, `Revisor`, `Service` class com adapters injetados
- `hermes.py`: `HermesAdapter` implementa mesma interface dos simulados
- `server.py`: Injeta adapters baseados em `CRIVO_MODO` env var

## References
- `crivo/engine.py`
- `crivo/service.py`
- `crivo/hermes.py`
- `crivo/server.py`

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