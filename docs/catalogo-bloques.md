# Catalogo de Bloques

> Documento vivo. Se actualiza cada vez que se agrega un bloque nuevo.
> Ultima actualizacion: 2026-03-19 (Fase 2: 3 bloques TS implementados)

---

## Bloques Python (Backend)

| Bloque | Descripcion | Dependencias | Instalar | Status |
|--------|-------------|-------------|----------|--------|
| `bloque-core` | Middleware, schemas, logging, health checks | fastapi, pydantic, structlog | `uv add bloque-core` | MVP |
| `bloque-auth` | JWT RS256, RBAC, brute force, TenantCredential | bloque-core, pyjwt, cryptography | `uv add bloque-auth` | MVP |
| `bloque-multitenant` | PostgreSQL RLS transparente via contextvars | bloque-core, sqlalchemy, asyncpg | `uv add bloque-multitenant` | MVP |
| `bloque-redis` | Cache + Streams + consumer groups | redis | `uv add bloque-redis` | Futuro |
| `bloque-gateway` | API Gateway con rate limiting y proxy | bloque-core, httpx | `uv add bloque-gateway` | Futuro |
| `bloque-ai-rag` | ChromaDB + LLM gateway multitenant | chromadb, httpx | `uv add bloque-ai-rag` | Futuro |
| `bloque-channels` | WhatsApp, Telegram, Email webhooks | bloque-core, httpx | `uv add bloque-channels` | Futuro |
| `bloque-notifications` | Email + push + templates | bloque-core | `uv add bloque-notifications` | Futuro |
| `bloque-automation` | Rule engine + condition evaluator | bloque-core | `uv add bloque-automation` | Futuro |

---

## Bloques TypeScript (Frontend)

| Bloque | Descripcion | Dependencias | Instalar | Status |
|--------|-------------|-------------|----------|--------|
| `@bloque/types` | TypeScript types base (entity, api, auth, tenant) | - | `pnpm add @bloque/types` | MVP |
| `@bloque/api-client` | Cliente HTTP con interceptors + token mgmt | @bloque/types, fetch nativo | `pnpm add @bloque/api-client` | MVP |
| `@bloque/ui` | Tailwind CSS preset + cn() utility + design tokens | clsx, tailwind-merge | `pnpm add @bloque/ui` | MVP |
| `@bloque/auth-react` | Hooks + providers + guards | @bloque/types, react | `pnpm add @bloque/auth-react` | Futuro |
| `@bloque/dashboard` | Layout: sidebar, header, tenant selector | @bloque/ui, @bloque/auth-react | `pnpm add @bloque/dashboard` | Futuro |

---

## Bloques Infra

| Bloque | Descripcion | Instalar | Status |
|--------|-------------|----------|--------|
| `bloque-docker-dev` | Docker Compose para desarrollo (PG + Redis) | Template Copier | Futuro |
| `bloque-docker-prod` | Docker Compose produccion + nginx | Template Copier | Futuro |
| `bloque-ci-github` | GitHub Actions (lint, test, publish) | Template Copier | Planificado |
| `bloque-ci-gitlab` | GitLab CI equivalente | Template Copier | Futuro |

---

## Origen de Cada Bloque

| Bloque | Origen | Ruta SSH original |
|--------|--------|------------------|
| bloque-core | 048 CRM (`crm_shared`) | `server005:.../shared/python/crm_shared/` |
| bloque-auth (JWT/RBAC) | 048 CRM | `server005:.../services/auth-service/` |
| bloque-auth (brute force) | 031 Domus | `server003:.../services/auth/core/models/user.py` |
| bloque-auth (credentials) | 031 Domus | `server003:.../services/auth/core/models/credential.py` |
| bloque-multitenant | Nuevo (validado por debates 740-743) | N/A - PostgreSQL RLS nativo |
| bloque-gateway | 048 CRM | `server005:.../services/api-gateway/` |
| bloque-redis | 048 CRM | `server005:.../shared/python/crm_shared/redis/` |
| bloque-ai-rag | 048 CRM | `server005:.../services/ai-service/` |
| bloque-channels | 048 CRM | `server005:.../services/channels-service/` |
| @bloque/ui | 048 CRM (migrado a shadcn) | `server005:.../frontend/packages/@crm/ui/` |
| @bloque/api-client | 048 CRM | `server005:.../frontend/packages/@crm/api-client/` |
| @bloque/types | 048 CRM | `server005:.../frontend/packages/@crm/types/` |

---

## Como Agregar un Bloque Nuevo

1. Crear directorio en `packages/python/bloque-xxx/` o `packages/typescript/bloque-xxx/`
2. Agregar `pyproject.toml` o `package.json` con dependencias
3. Implementar codigo con tests
4. Agregar entrada en esta tabla
5. Crear receta si el bloque habilita un caso de uso nuevo
6. PR + review + merge a main
