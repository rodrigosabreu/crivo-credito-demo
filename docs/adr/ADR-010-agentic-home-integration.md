# ADR-010: Integração com Agentic-Home (skills, templates, catálogo)

## Status
Proposed

## Contexto
O Agentic-Home (`/opt/data/projects/agentic-home`) é o hub central para engenharia assistida por IA, provendo:
- Skills compartilhadas: descoberta, arquitetura, desenvolvimento, qualidade
- Templates padronizados: handoff.md, adr.md
- Catálogo de projetos: `projects/catalogo.md`
- Documentação de governança, arquitetura, onboarding
- Mecanismos de descoberta e coordenação entre projetos

O projeto Crivo Crédito Demo deve integrar-se ao ecossistema Home para aproveitar skills, templates e governança compartilhada.

## Decisão
Integrar com Agentic-Home via:
1. **Skills carregáveis via `skill_view()`**:
   - `descoberta` — Exploração de problemas, requisitos, cenários, critérios de aceite
   - `arquitetura` — Design técnico, trade-offs, ADRs, dependências, riscos técnicos
   - `desenvolvimento` — Padrões implementação, testes, CI/CD
   - `qualidade` — Validação, testes, revisão código, observabilidade
   - `onboard-ai-dlc` — Esta integração (workflows Diagnose→Plan→Baseline→Integrate→Validate)
2. **Templates referenciados, não copiados**:
   - `agentic-home/templates/handoff.md` → Base para `handoff.md` do projeto (estendido com campos AI-DLC)
   - `agentic-home/templates/adr.md` → Base para ADRs do projeto (estendido com campos AI-DLC: Compliance Impact, AI-DLC Impact)
3. **Catálogo sincronizado**: Projeto registrado em `agentic-home/projects/catalogo.md` (já feito: commit `54a2024`)
4. **Governança referenciada**: `agentic-home/docs/governanca.md` para stage gates, matriz de permissões
5. **Onboarding referenciado**: `agentic-home/docs/onboarding.md` para onboarding self-service
6. **AGENTS.md do projeto** aponta para Home: seção "Integração com Agentic Home" já existe, será estendida com seção "AI-DLC Workspace"

## Alternativas Consideradas

| Alternativa | Prós | Contras | Decisão |
|-------------|------|---------|---------|
| 1. Copiar templates/skills para o projeto | Autônomo, sem dependência externa | Duplicação, divergência, manutenção múltipla, viola princípio Home | Rejeitada |
| 2. Referenciar Home mas não usar skills | Leve | Perde valor das skills compartilhadas, padronização | Rejeitada |
| 3. Integrar fully: skills + templates + catálogo + governança (escolhida) | DRY, padronizado, governança única, skills reutilizáveis | Dependência do Home disponível | **Proposta** |

## Consequências

### Positivas
- Skills reutilizáveis entre projetos — aprendizado compartilhado
- Templates únicos — consistência, atualização centralizada
- Catálogo único — descoberta de projetos padronizada
- Governança unificada — stage gates, aprovações, compliance
- Onboarding self-service — novos agentes/equipes usam docs Home

### Negativas
- Dependência do Agentic-Home acessível (`/opt/data/projects/agentic-home`)
- Skills devem ser carregadas explicitamente (`skill_view()`)
- Versionamento: mudanças no Home afetam projetos

### Riscos
- Home indisponível (caminho errado, movido) — skills falham
- Conflito de namespace skills (Home vs projeto)
- Templates Home mudam e quebram projetos

### Mitigações
- Caminho Home documentado no AGENTS.md do projeto
- Namespace `agentic-home:` vs projeto — skills Home carregadas via `skill_view(name='descoberta')`
- Templates referenciados por caminho absoluto; projetos fixam versão se necessário

## Impacto de Compliance
- [x] Outro: Governança centralizada suporta auditoria cross-projeto
- [ ] LGPD: Skills/templates não processam dados pessoais

## Impact AI-DLC
- **Eval gates afetados**: Validate workflow testa integração Home (skills carregáveis, templates referenciam Home)
- **Pipeline changes**: CI/CD futuro pode validar `skill_view()` success
- **Observabilidade needs**: Métricas de uso de skills Home por projeto
- **Model routing changes**: Skills podem usar LLMs via Hermes — roteamento centralizado
- **Cost impact**: Zero adicional (Home já existe)

## Implementation Notes
- AGENTS.md do projeto: Seção "Integração com Agentic Home" (já existe, linhas 103-125)
- Nova seção "AI-DLC Workspace" referenciará `aidlc/` e skills
- `handoff.md` estendido com campos AI-DLC referencia template Home
- ADRs usam template Home estendido (campos Compliance Impact, AI-DLC Impact)
- Catálogo: `agentic-home/projects/catalogo.md` já tem entrada `crivo-credito-demo`

## References
- Agentic-Home: `AGENTS.md`, `projects/catalogo.md`, `skills/`, `templates/`, `docs/`
- Skill: `onboard-ai-dlc` (integração com skills descoberta, arquitetura, desenvolvimento, qualidade)
- Diagnose Report: `diagnose-report.md` seção 6 (Integração com Skills Home: ✅ Referenciada)
- Integration Plan: `integration-plan.md` seção 8.2 (ADR-010)

---

## History
| Date | Version | Author | Change |
|------|---------|--------|--------|
| 2026-11-23 | 1.0 | Polaris (PM) | Proposta inicial baseada em integration-plan.md |

---

## Approval
| Role | Name | Date | Signature |
|------|------|------|-----------|
| Author | Polaris (PM) | 2026-11-23 | Proposta |
| Reviewer | — | — | Pendente |
| Approver | Rodrigo (PM) | — | Pendente (Gate 2) |