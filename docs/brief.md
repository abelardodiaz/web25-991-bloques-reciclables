# Brief: 991 Bloques Reciclables (Open Source)

## Vision

Caja de legos open source para construir cualquier tipo de proyecto web/API. No es un "SaaS template" rigido - es un ecosistema de bloques composables donde cada proyecto toma solo lo que necesita.

Multi-stack (Python + TypeScript), multi-framework (FastAPI, Django, Next.js), y 100% publico.

## Escenarios de Uso

| Escenario | Bloques que toma | Comando |
|-----------|-----------------|---------|
| SaaS multitenant completo | core + auth + multitenant + billing + ui | `copier copy template-saas-full .` |
| API REST simple | core + un servicio FastAPI | `uv add bloque-core` |
| MVP sin login | core + ui (sin auth) | `uv add bloque-core && pnpm add @bloque/ui` |
| Dashboard Django + Next.js | core-django + auth-django + ui | `uv add bloque-core-django` |
| Bot de WhatsApp | core + channels + ai | `uv add bloque-core bloque-channels bloque-ai` |
| Landing + API | ui + un endpoint | `pnpm add @bloque/ui` |

## Principios

1. **Composable**: Cada bloque funciona independiente. No hay dependencias forzadas.
2. **Multi-stack**: FastAPI, Django, Next.js, React - los bloques se adaptan.
3. **Crecimiento organico**: Empezar con pocos bloques, agregar conforme surjan proyectos.
4. **Packages + Templates**: Los bloques son packages versionados. Los templates son scaffolding que los importa.
5. **Greenfield y Brownfield**: Sirve para proyectos nuevos Y para migrar existentes.
6. **Open source**: MIT license. Sin secrets, sin logica de negocio propietaria.

## Origen

Analisis de dos proyectos SaaS maduros:
- **Domus SaaS (031)**: Django + FastAPI, 9 microservicios, inmobiliario
- **CRM Multi-tenant (048)**: FastAPI puro, 11 microservicios, CRM omnicanal

Validado por debates multi-IA (Gemini + DeepSeek) con web search - API 900 tickets 740-743.

Ver `analisis-031-vs-048.md` para el analisis completo y `plan-arquitectura.md` para la arquitectura validada.

## Diferencia con 996

996 es privado (orquestacion, preparativos, API keys). 991 es publico (bloques de codigo reutilizable).

Ver `991-vs-996.md` para comparativa detallada.

## Stack

| Capa | Herramientas |
|------|-------------|
| Python packages | uv workspaces + PyPI |
| TypeScript packages | pnpm workspaces + Turborepo |
| Templates | Copier composable |
| Multitenant | PostgreSQL RLS nativo |
| CI/CD | GitHub Actions |
| Licencia | MIT |

## Ubicacion

- Repo: `prweb/public/web25-991-bloques-reciclables`
- Preparativos (este directorio): `prweb/web25-996-claude-code-agentes-demo/docs/991-bloques-reciclables/`

## Status

En preparativos. Analisis de 031 vs 048 completado. Arquitectura validada por debates multi-IA. Pendiente: arranque formal del proyecto.
