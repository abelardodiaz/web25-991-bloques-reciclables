# Roadmap: 991 Bloques Reciclables

---

## Fase 1: Core (MVP)

Valor dia 1. Un developer puede instalar bloques basicos y tener una API multitenant funcional.

- [ ] Estructura monorepo (uv + pnpm + Turborepo)
- [ ] `bloque-core` - Middleware, schemas, logging, health
- [ ] `bloque-auth` - JWT RS256, RBAC, brute force, TenantCredential
- [ ] `bloque-multitenant` - PostgreSQL RLS transparente via contextvars
- [ ] `examples/api-simple` - Ejemplo funcional minimo
- [ ] README publico + LICENSE MIT
- [ ] CI/CD basico (GitHub Actions)
- [ ] Publicacion en PyPI (packages Python)

---

## Fase 2: Frontend + Templates

Bloques TypeScript y templates Copier para scaffolding completo.

- [ ] `@bloque/ui` - shadcn/ui componentes base
- [ ] `@bloque/api-client` - Cliente HTTP con interceptors + token management
- [ ] `@bloque/types` - TypeScript types base (auth, pagination, etc)
- [ ] `@bloque/auth-react` - Hooks + providers + guards
- [ ] Template Copier: base (Turborepo + pnpm + uv)
- [ ] Template Copier: backend-fastapi
- [ ] Template Copier: frontend-nextjs
- [ ] Publicacion en npm (packages TS)

---

## Fase 3: Plugins por demanda

Se agregan conforme surjan necesidades en proyectos reales.

- [ ] `bloque-redis` - Cache + Streams + consumer groups
- [ ] `bloque-gateway` - API Gateway con rate limiting, proxy
- [ ] `bloque-ai-rag` - ChromaDB + LLM gateway multitenant
- [ ] `bloque-channels` - WhatsApp, Telegram, Email webhooks
- [ ] `bloque-notifications` - Email + push + templates
- [ ] `bloque-automation` - Rule engine + condition evaluator
- [ ] `bloque-billing` - Stripe integration
- [ ] `@bloque/dashboard` - Layout base con sidebar, header, tenant selector

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
| Bloques disponibles Fase 2 | 7 (+4 frontend) |
| Tests passing | 100% en CI |
| Documentacion por bloque | README + ejemplo |
