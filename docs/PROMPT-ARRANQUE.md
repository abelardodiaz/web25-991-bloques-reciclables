# PROMPT-ARRANQUE: 991 Bloques Reciclables

> Instrucciones para el agente 991 al arrancar el proyecto.
> Ubicacion destino: `C:\Users\abela\prweb\public\web25-991-bloques-reciclables`

---

## Contexto Operativo

**Entorno:** Claude Code corre en Windows, pero TODO el desarrollo (instalar librerias, correr tests, SSH) se hace via WSL.
- Path Windows: `C:\Users\abela\prweb\public\web25-991-bloques-reciclables`
- Path WSL: `/mnt/c/Users/abela/prweb/public/web25-991-bloques-reciclables`
- Mismas carpetas, accesibles desde ambos lados (la magia de WSL)

**SSH a servers fuente (siempre via WSL):**
- `wsl ssh server005` -> 048 CRM: `/home/ubuntu/projects/web25-048-crm/`
  - `shared/python/crm_shared/` -> base para bloque-core (23+ archivos)
  - `services/auth-service/` -> base para bloque-auth (JWT, RBAC)
  - `services/api-gateway/src/main.py` -> referencia para bloque-gateway
  - `frontend/packages/` -> base para @bloque/ui, @bloque/api-client, @bloque/types
- `wsl ssh server003` -> 031 Domus: `/home/ubuntu/web25-031-domus-saas/`
  - `backend/services/auth/core/models/credential.py` -> TenantCredential + Fernet
  - `backend/services/auth/core/models/user.py` -> brute force protection
  - `backend/shared/models/base.py` -> SoftDeleteMixin

**Skills disponibles:**
- `/consultar-900` - Debates multi-IA para validar decisiones de arquitectura
- `/consultar-99999` - Registrar proyecto en Project Manager
- Nota: 996 distribuye skills a este proyecto con `/distribuir-skills` (996 lo ejecuta, no 991)

**Politicas:**
- SIEMPRE usar pnpm (NO npm)
- SIEMPRE push a ambos remotes: `git push github main && git push origin main`
- SIEMPRE actualizar PROJECT.yaml en cada commit

---

## Paso 1: Repositorios (YA CREADOS)

Los repos publicos ya existen:
- GitHub: https://github.com/abelardodiaz/web25-991-bloques-reciclables
- GitLab: https://gitlab.com/abelardodiaz/web25-991-bloques-reciclables

## Paso 2: Inicializar proyecto

CLAUDE.md y PROJECT.yaml ya estan copiados en la carpeta. Solo inicializar git:

```bash
cd /mnt/c/Users/abela/prweb/public/web25-991-bloques-reciclables

git init
git remote add origin git@gitlab.com:abelardodiaz/web25-991-bloques-reciclables.git
git remote add github git@github.com:abelardodiaz/web25-991-bloques-reciclables.git
```

## Paso 3: Estructura base del monorepo

```bash
# CLAUDE.md y PROJECT.yaml ya estan en la raiz

# Python workspace (uv)
mkdir -p packages/python/bloque-core/src/bloque_core
mkdir -p packages/python/bloque-core/tests
mkdir -p packages/python/bloque-auth/src/bloque_auth
mkdir -p packages/python/bloque-auth/tests
mkdir -p packages/python/bloque-multitenant/src/bloque_multitenant
mkdir -p packages/python/bloque-multitenant/tests

# TypeScript workspace (pnpm + Turborepo)
mkdir -p packages/typescript/bloque-ui/src
mkdir -p packages/typescript/bloque-api-client/src
mkdir -p packages/typescript/bloque-types/src

# Templates Copier
mkdir -p templates/template-base
mkdir -p templates/template-backend-fastapi
mkdir -p templates/template-frontend-nextjs

# Ejemplos
mkdir -p examples/api-simple
mkdir -p examples/saas-multitenant

# Docs
mkdir -p docs
```

## Paso 4: Configurar uv workspace (Python)

Crear `pyproject.toml` en la raiz:

```toml
[project]
name = "bloques-reciclables"
version = "0.1.0"
description = "Ecosistema open source de bloques de codigo reciclables"
requires-python = ">=3.11"

[tool.uv.workspace]
members = ["packages/python/*"]

[tool.ruff]
target-version = "py311"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B"]

[tool.pytest.ini_options]
testpaths = ["packages/python"]
asyncio_mode = "auto"
```

Cada package Python tiene su propio `pyproject.toml`:

```toml
# packages/python/bloque-core/pyproject.toml
[project]
name = "bloque-core"
version = "0.1.0"
description = "Core utilities: middleware, schemas, logging, health checks"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "pydantic>=2.0",
    "pydantic-settings>=2.0",
    "structlog>=24.0",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-asyncio>=0.24", "httpx>=0.27"]
```

## Paso 5: Configurar pnpm + Turborepo (TypeScript)

```yaml
# pnpm-workspace.yaml
packages:
  - "packages/typescript/*"
  - "examples/*"
```

```json
// turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**"]
    },
    "test": {
      "dependsOn": ["build"]
    },
    "lint": {}
  }
}
```

```json
// package.json (raiz)
{
  "name": "bloques-reciclables",
  "private": true,
  "scripts": {
    "build": "turbo run build",
    "test": "turbo run test",
    "lint": "turbo run lint"
  },
  "devDependencies": {
    "turbo": "^2.0.0",
    "typescript": "^5.7.0"
  }
}
```

## Paso 6: Crear bloque-core (MVP)

El primer bloque. Incluye:

- `middleware/request_id.py` - Inyecta X-Request-ID en cada request
- `middleware/timing.py` - Mide duracion de cada request
- `schemas/base.py` - PaginatedResponse[T], HealthResponse, ErrorResponse
- `logging/setup.py` - structlog configurado con request ID
- `health/router.py` - Endpoint /health

Basado en `crm_shared` de 048. Para extraer el codigo fuente:

```bash
# Copiar crm_shared desde server005 via WSL
wsl bash -c 'scp -r server005:/home/ubuntu/projects/web25-048-crm/shared/python/crm_shared/ /tmp/crm_shared_ref/'
```

Adaptar: renombrar imports de `crm_shared` a `bloque_core`, limpiar referencias a CRM, hacer generico.

## Paso 7: Crear bloque-auth (MVP)

- `jwt/manager.py` - JWT RS256 con tenant_id y roles en payload
- `rbac/permissions.py` - RBAC con dependencias FastAPI
- `brute_force/protection.py` - Proteccion contra fuerza bruta (de 031)
- `credentials/fernet.py` - TenantCredential con Fernet AES-256 (de 031)

Para extraer codigo fuente:

```bash
# JWT y RBAC de 048
wsl bash -c 'scp -r server005:/home/ubuntu/projects/web25-048-crm/services/auth-service/src/ /tmp/auth_048_ref/'

# Brute force y TenantCredential de 031
wsl bash -c 'scp server003:/home/ubuntu/web25-031-domus-saas/backend/services/auth/core/models/credential.py /tmp/credential_031_ref.py'
wsl bash -c 'scp server003:/home/ubuntu/web25-031-domus-saas/backend/services/auth/core/models/user.py /tmp/user_031_ref.py'
```

Adaptar: extraer solo la logica reutilizable, limpiar imports especificos de cada proyecto, hacer generico.

## Paso 8: Crear bloque-multitenant (MVP)

- `rls/middleware.py` - PostgreSQL RLS transparente via contextvars
- `rls/setup.py` - SQL para crear policies RLS
- `context/tenant.py` - TenantContext con contextvar

Este bloque es NUEVO (no existe en 031 ni 048). Disenar desde cero basado en el patron validado en debates API 900 (tickets 740-743). Ver `plan-arquitectura.md` seccion "Multitenant: PostgreSQL RLS transparente".

## Paso 9: Crear example/api-simple

Un ejemplo funcional minimo:

```python
# examples/api-simple/main.py
from fastapi import FastAPI
from bloque_core.middleware import RequestIDMiddleware, TimingMiddleware
from bloque_core.health import health_router
from bloque_core.logging import setup_logging

app = FastAPI(title="API Simple con Bloques")
setup_logging()
app.add_middleware(RequestIDMiddleware)
app.add_middleware(TimingMiddleware)
app.include_router(health_router)

@app.get("/")
async def root():
    return {"message": "Funcionando con bloque-core"}
```

## Paso 10: README publico + LICENSE

- `README.md` con:
  - Que es, para que sirve
  - Quick start (uv add bloque-core)
  - Lista de bloques disponibles
  - Link a recetas
  - Contributing guide basico
- `LICENSE` - MIT
- `.gitignore` - Python + Node + uv + pnpm

## Paso 11: CI/CD basico

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync --all-packages
      - run: uv run pytest
      - run: uv run ruff check .

  typescript:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
      - run: pnpm install
      - run: pnpm run lint
      - run: pnpm run test
```

## Paso 12: Commit inicial + push

```bash
git add -A
git commit -m "feat: initial monorepo structure with bloque-core, bloque-auth, bloque-multitenant"
git push github main && git push origin main
```

---

## Verificacion Post-Arranque

- [ ] `wsl bash -c 'cd /mnt/c/.../web25-991-bloques-reciclables && uv sync'` funciona sin errores
- [ ] `pnpm install` funciona sin errores
- [ ] `wsl bash -c '... && uv run pytest'` pasa en bloque-core
- [ ] `examples/api-simple` levanta con `uv run uvicorn`
- [ ] README.md tiene instrucciones claras
- [ ] LICENSE es MIT
- [ ] CI/CD pasa en GitHub Actions
- [ ] Registrar proyecto en Project Manager: `/consultar-99999`

## Documentos de Referencia (en esta misma carpeta de preparativos)

- `brief.md` - Vision y principios del proyecto
- `analisis-031-vs-048.md` - Analisis de codigo fuente reciclable
- `plan-arquitectura.md` - Arquitectura validada por debates multi-IA
- `estructura-proyecto.md` - Arbol completo de directorios
- `catalogo-bloques.md` - Lista de todos los bloques planificados
- `ROADMAP.md` - Fases del proyecto
- `recetas/` - Ejemplos de combinaciones de bloques
- `991-vs-996.md` - Diferencia entre este proyecto y 996
- `por-que-open-source.md` - Razonamiento open source
- `relacion-996-991.md` - Como interactuan 996 y 991
