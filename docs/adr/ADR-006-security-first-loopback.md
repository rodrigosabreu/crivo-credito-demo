# ADR-006: Security-first: loopback only, origin validation, CSRF protection

## Status
Implemented

## Contexto
A aplicação expõe API HTTP local. Mesmo sendo POC local, deve seguir princípios de segurança: não expor na rede, validar origem das requisições, proteger contra CSRF.

## Decisão
1. **Loopback only**: Bind `127.0.0.1:8000` — não acessível externamente
2. **Origin validation**: `server.py` valida headers `Origin` e `Referer` — rejeita se não `http://127.0.0.1:8000` ou `http://localhost:8000`
3. **CSRF protection** (modo demo): `demo.py` implementa token CSRF double-submit cookie + header
4. **Sem autenticação/autorização**: POC não endurecida — documentado explicitamente
5. **Modo Hermes opt-in**: Requer gateway rodando em loopback + chaves de acesso via env vars

## Alternativas Consideradas
| Alternativa | Prós | Contras | Decisão |
|-------------|------|---------|---------|
| 1. Bind 0.0.0.0 (todas interfaces) | Acesso remoto fácil | Inseguro, expõe API local | Rejeitada |
| 2. Sem validação origem | Simples | Vulnerável a CSRF, DNS rebinding | Rejeitada |
| 3. Loopback + origin validation + CSRF | Seguro por padrão, defense-in-depth | Mais código | **Aceita** |

## Consequências
### Positivas
- Segurança por padrão: não expõe serviços
- Defense-in-depth: múltiplas camadas
- Documentação clara de limitações (sem auth, POC only)

### Negativas
- Não testável remotamente sem túnel (cloudflared)
- CSRF apenas no modo demo (não no modo simples)

### Riscos
- Túnel cloudflared expõe temporariamente (mitigado: auth no túnel)
- Falso senso de segurança se usado indevidamente

### Mitigações
- `.gitignore` ignora binários e segredos
- Documentação explícita: "POC não endurecida", "Não usar com dados reais"

## Impacto de Compliance
- [ ] Regulatório financeiro
- [ ] LGPD (Lei 13.709) — Princípio privacy by design
- [ ] SOX
- [ ] PCI-DSS
- [ ] ANBIMA
- [ ] CMN 4.658
- [x] Outro: Security-by-design para POC local

## Impacto AI-DLC
- **Eval gates afetados**: Nenhum (decisão pré-existente)
- **Pipeline changes**: N/A
- **Observabilidade needs**: Logs de requisições rejeitadas (origin/CSRF)
- **Model routing changes**: N/A
- **Cost impact**: Zero

## Implementation Notes
- `server.py`: `validar_origem()` — verifica Origin/Referer headers
- `server.py`: Bind `127.0.0.1:8000` hardcoded
- `demo.py`: CSRF token via cookie + header `X-CSRF-Token`
- `hermes.py`: Gateway Hermes também loopback, chaves via `CRIVO_HERMES_CHAVE_*`

## References
- `crivo/server.py` — validação origem, bind loopback
- `demo.py` — CSRF implementation
- `crivo/hermes.py` — cliente gateway Hermes

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