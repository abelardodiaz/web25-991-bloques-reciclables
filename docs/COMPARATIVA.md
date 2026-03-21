# ulfblk vs Alternativas

> Comparativa honesta para que elijas la herramienta correcta para tu proyecto.

## Tabla Comparativa

| Caracteristica | ulfblk | Django | Laravel | SaaS Pegasus | ShipFast | Supabase | create-t3-app |
|---------------|--------|--------|---------|-------------|----------|----------|---------------|
| **Stack** | FastAPI + Next.js | Django (Python) | PHP | Django | Next.js | PostgreSQL + JS | Next.js + tRPC |
| **Modelo** | Paquetes composables | Framework monolitico | Framework monolitico | Boilerplate (codigo fuente) | Boilerplate (codigo fuente) | BaaS (hosted) | Generador |
| **Multitenancy** | PostgreSQL RLS transparente | Manual o django-tenants | Manual o Tenancy for Laravel | Incluido | No incluido | RLS nativo | No incluido |
| **Auth** | JWT RS256 + RBAC composable | django.contrib.auth | Laravel Sanctum/Passport | Incluido | NextAuth | Supabase Auth | NextAuth |
| **Base de datos** | SQLAlchemy async + mixins composables | Django ORM | Eloquent ORM | Django ORM | Prisma | PostgreSQL directo | Prisma |
| **Actualizaciones** | `uv add ulfblk-core@latest` | Actualizar framework completo | Actualizar framework completo | Git merge manual | Git merge manual | Automatico (hosted) | Re-generar |
| **Personalizacion** | Extender/subclasear | Modificar internals | Modificar internals | Codigo es tuyo | Codigo es tuyo | Limitado a su API | Codigo es tuyo |
| **Precio** | Gratis (MIT) | Gratis | Gratis | $249+ USD | $179+ USD | Free tier + pago | Gratis |
| **Tests incluidos** | Si (pytest plugin) | Si (TestCase) | Si (PHPUnit) | Si | Parcial | No | No |

## vs Ecosistemas FastAPI Existentes

| Proyecto | Que cubre | Stars | Diferencia con ulfblk |
|----------|-----------|-------|----------------------|
| **FastAPI Users** | Solo auth (registro, login, OAuth2, JWT) | ~4.5k | Solo auth. ulfblk cubre 17 areas |
| **SQLModel** | Solo ORM (Pydantic + SQLAlchemy) | ~12k | Solo DB. No tiene auth, multitenancy, testing, billing |
| **Piccolo** | ORM + Admin + Auth (paquetes separados) | ~1.5k | ORM propietario. ulfblk usa SQLAlchemy estandar |
| **full-stack-fastapi-template** | Template con estructura sugerida | ~14k | Template que copias, no paquetes pip actualizables |
| **ulfblk** | Auth + DB + Multitenancy + Billing + Testing + 12 mas | 17 paquetes | Unico ecosistema composable completo para FastAPI |

**Hallazgo clave:** No existe un paquete de multitenancy con PostgreSQL RLS para FastAPI. `django-tenants` lo resuelve para Django, Supabase lo tiene en su plataforma, pero para FastAPI puro nadie lo ofrece excepto ulfblk.

## Killer Features de ulfblk

### 1. Mixins Composables
No te fuerza modelos. Tu defines tus propios modelos y compones lo que necesitas:
```python
class User(Base, TimestampMixin, SoftDeleteMixin):
    # Tu modelo, tus campos, tus relaciones
```

### 2. RLS Transparente (PostgreSQL)
Multitenancy via PostgreSQL Row-Level Security. Con PostgreSQL + `apply_rls(engine)`, la DB filtra automaticamente por tenant. Con SQLite (desarrollo), el filtro es manual en las queries. El ejemplo usa SQLite por zero-config.

### 3. Pytest Plugin Auto-register
`uv add --dev ulfblk-testing` y las fixtures estan disponibles sin configurar nada. JWT test tokens, HTTP clients autenticados, DB in-memory.

### 4. Config Centralizada
Todas las settings heredan de `BloqueSettings`. Un `.env` con `BLOQUE_*` configura todo el ecosistema.

### 5. Zero-Config para Desarrollo
SQLite por defecto (sin instalar PostgreSQL). Cambia a PostgreSQL con un env var cuando estes listo para produccion.

### 6. Migraciones Alembic Integradas
`uv add ulfblk-db[migrations]` y tienes CLI para init, create, upgrade, downgrade. Templates async-ready pre-configurados.

### 7. Admin Panel con react-admin
`@ulfblk/admin` provee DataProvider + AuthProvider. 5 lineas para tener CRUD admin con login, permisos, y tenant isolation.

## Cuando Usar ulfblk

- Estas haciendo un SaaS multitenant con FastAPI
- Necesitas iterar rapido y no quieres configurar JWT/RBAC/RLS desde cero
- Prefieres paquetes composables sobre un framework monolitico
- Tu equipo ya conoce Python + SQLAlchemy + FastAPI

## Cuando NO Usar ulfblk

- **Necesitas maximo control**: los boilerplates (Pegasus, ShipFast) te dan el codigo fuente completo para modificar. ulfblk te da paquetes - si necesitas cambiar la logica interna, debes forkear o subclasear
- **Tu stack no es Python**: si tu equipo es PHP (Laravel) o Ruby (Rails), usa lo que ya conocen
- **No necesitas multitenancy**: si tu app es single-tenant, Django o FastAPI vanilla es mas simple
- **Quieres hosting incluido**: Supabase te da DB + Auth + Storage + Edge Functions sin infrastructure. ulfblk requiere tu propio servidor
- **Proyecto muy grande**: para empresas con equipos grandes, un framework opinado (Django, Rails) con su ecosistema maduro es mas seguro

## Limitaciones Conocidas

1. **Ecosistema joven**: no tiene la madurez de Django (20 anios) o Laravel (12 anios)
2. ~~Sin migraciones automaticas~~: Resuelto - `ulfblk-db[migrations]` integra Alembic con CLI y templates async-ready
3. ~~Sin admin panel~~: Resuelto - `@ulfblk/admin` provee DataProvider + AuthProvider para react-admin
4. **Comunidad pequena**: sin Stack Overflow threads, sin tutoriales de terceros todavia
5. **Solo Python + TypeScript**: si necesitas Go, Rust, Java - no es para ti
