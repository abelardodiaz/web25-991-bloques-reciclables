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

## Killer Features de ulfblk

### 1. Mixins Composables
No te fuerza modelos. Tu defines tus propios modelos y compones lo que necesitas:
```python
class User(Base, TimestampMixin, SoftDeleteMixin):
    # Tu modelo, tus campos, tus relaciones
```

### 2. RLS Transparente
Multitenancy via PostgreSQL Row-Level Security. El developer nunca escribe `WHERE tenant_id = ...` - la DB lo filtra automaticamente.

### 3. Pytest Plugin Auto-register
`uv add --dev ulfblk-testing` y las fixtures estan disponibles sin configurar nada. JWT test tokens, HTTP clients autenticados, DB in-memory.

### 4. Config Centralizada
Todas las settings heredan de `BloqueSettings`. Un `.env` con `BLOQUE_*` configura todo el ecosistema.

### 5. Zero-Config para Desarrollo
SQLite por defecto (sin instalar PostgreSQL). Cambia a PostgreSQL con un env var cuando estes listo para produccion.

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
2. **Sin migraciones automaticas**: Alembic no esta integrado aun, debes manejarlo tu
3. **Sin admin panel**: Django tiene django-admin built-in, ulfblk no
4. **Comunidad pequena**: sin Stack Overflow threads, sin tutoriales de terceros todavia
5. **Solo Python + TypeScript**: si necesitas Go, Rust, Java - no es para ti
