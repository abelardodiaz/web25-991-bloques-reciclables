# Roadmap: 991 Bloques Reciclables

---

## Fase 1: Core (MVP)

Valor dia 1. Un developer puede instalar bloques basicos y tener una API multitenant funcional.

- [x] Estructura monorepo (uv + pnpm + Turborepo)
- [x] `bloque-core` - Middleware, schemas, logging, health
- [x] `bloque-auth` - JWT RS256, RBAC, brute force, TenantCredential
- [x] `bloque-multitenant` - PostgreSQL RLS transparente via contextvars
- [x] `examples/api-simple` - Ejemplo funcional minimo
- [x] README publico + LICENSE MIT
- [x] CI/CD basico (GitHub Actions)
- [ ] Publicacion en PyPI (packages Python) - pyproject.toml listos, pendiente cuenta PyPI + `uv publish`

---

## Fase 2: Frontend + Templates

Bloques TypeScript y templates Copier para scaffolding completo.

- [x] `@bloque/types` - TypeScript types base (entity, api, auth, tenant)
- [x] `@bloque/api-client` - Cliente HTTP con interceptors + token management (fetch nativo, zero deps)
- [x] `@bloque/ui` - Tailwind CSS preset + cn() utility + design tokens
- [x] `@bloque/auth-react` - Hooks + providers + guards (React Context, JWT decode, RBAC guards)
- [x] Template Copier: base (Turborepo + pnpm + uv)
- [x] Template Copier: backend-fastapi
- [x] Template Copier: frontend-nextjs
- [ ] Publicacion en npm (packages TS)

---

## Fase 3: Plugins por demanda

Se agregan conforme surjan necesidades en proyectos reales.

- [x] `bloque-redis` - Cache + Streams + consumer groups
- [x] `bloque-gateway` - API Gateway con rate limiting, proxy, circuit breaker
- [x] `bloque-ai-rag` - ChromaDB + LLM gateway multitenant
- [x] `bloque-channels` - WhatsApp, Telegram, Email webhooks
- [x] `bloque-notifications` - Email + push + templates
- [x] `bloque-automation` - Rule engine + condition evaluator
- [x] `bloque-billing` - Stripe integration
- [x] `@bloque/dashboard` - Layout base con sidebar, header, data tables, nav, tenant selector

---

## Fase 4: Infra + DevOps

Bloques de infraestructura para desarrollo y produccion.

- [ ] `bloque-docker-dev` - Docker Compose para desarrollo (PostgreSQL + Redis)
- [ ] `bloque-docker-prod` - Docker Compose produccion + nginx
- [ ] `bloque-ci-github` - GitHub Actions completo (lint, test, publish)
- [ ] `bloque-ci-gitlab` - GitLab CI equivalente

---

## Fase 5: Migracion (opcional)

Migrar componentes de proyectos existentes al ecosistema de bloques.

- [ ] Strangler Fig para 048 CRM -> usar bloques en lugar de crm_shared
- [ ] Strangler Fig para 031 Domus -> reemplazar shared code con bloques
- [ ] Documentar patron de migracion brownfield

---

## Metricas de Exito

| Metrica | Target |
|---------|--------|
| Tiempo para crear API multitenant | < 1 hora |
| Bloques disponibles Fase 1 | 3 (core, auth, multitenant) |
| Bloques disponibles Fase 2 | 7 (+4 frontend) + 3 templates |
| Tests passing | 100% en CI |
| Documentacion por bloque | README + ejemplo |
