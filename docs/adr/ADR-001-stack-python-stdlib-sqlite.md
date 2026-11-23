# ADR-001: Stack tecnológica Python 3.10+ stdlib + SQLite

## Status
Implemented

## Contexto
O projeto precisa de uma stack minimalista, zero dependências externas, que rode imediatamente em qualquer ambiente Python 3.10+. A aplicação é uma POC local de análise de crédito sintética.

## Decisão
- Linguagem: Python 3.10+ (apenas stdlib)
- HTTP Server: `http.server.ThreadingHTTPServer` (bind 127.0.0.1:8000)
- Banco de dados: SQLite embarcado (`crivo.sqlite3`)
- Zero dependências externas (sem pip, requirements.txt, pyproject.toml)
- Document processing: N/A (dados sintéticos em memória)

## Alternativas Consideradas
| Alternativa | Prós | Contras | Decisão |
|-------------|------|---------|---------|
| 1. Python + FastAPI + Uvicorn | Framework moderno, async | Dependências externas, build necessário | Rejeitada |
| 2. Python stdlib apenas | Zero deps, roda imediato, portável | Sem async nativo, menos features | **Aceita** |
| 3. Java Spring Boot | Enterprise ready | Heavyweight, build complexo | Rejeitada |

## Consequências
### Positivas
- Execução imediata: `python run_server.py` sem setup
- Portabilidade total (qualquer Python 3.10+)
- Zero superfície de ataque de supply chain
- Ideal para POC/demo local

### Negativas
- Sem async/await nativo no HTTP server
- Limitação de concorrência (threading apenas)
- Sem validação automática de schema (Pydantic)
- Sem OpenAPI/Swagger automático

### Riscos
- Se projeto evoluir para produção, migração custosa
- Testes manuais mais frequentes

### Mitigações
- Documentar claramente: "POC local, exclusivamente sintética"
- Modo Hermes opt-in para extensibilidade futura

## Impacto de Compliance
- [ ] Regulatório financeiro (CVM, Bacen, etc.)
- [ ] LGPD (Lei 13.709)
- [ ] SOX (Lei 11.941/2009)
- [ ] PCI-DSS
- [ ] ANBIMA
- [ ] CMN 4.658
- [x] Outro: Zero dados reais — catálogo sintético fixo

## Impacto AI-DLC
- **Eval gates afetados**: Nenhum (decisão pré-existente)
- **Pipeline changes**: N/A
- **Observabilidade needs**: Logs básicos stdout
- **Model routing changes**: N/A
- **Cost impact**: Zero (stdlib only)

## Implementation Notes
- Arquivos: `engine.py`, `service.py`, `server.py`, `run_server.py`, `hermes.py`
- Entry point: `run_server.py` (ajusta sys.path e importa server)
- SQLite: `crivo.sqlite3` com tabelas `runs` + `events`

## References
- `crivo/engine.py` — Motor de regras
- `crivo/service.py` — Orquestração
- `crivo/server.py` — HTTP server
- `run_server.py` — Entry point

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