# CLAUDE.md - Bloques Reciclables (web25-991)

## PROJECT.yaml - IMPORTANTE

Este proyecto tiene un archivo `PROJECT.yaml` en la raiz. Es leido por el Project Manager (99999) para monitorear el estado.

**Cuando actualizar:**
- Cambio de version -> actualiza `project.version`
- Siempre actualiza `updated_at` y `updated_by: claude-991`

**NO modificar sin razon:**
- `project.code` - identificador unico
- `server.base_path` - ruta del proyecto

---

## Descripcion

Ecosistema open source de bloques de codigo reciclables. Caja de legos multi-stack (Python + TypeScript) para construir cualquier tipo de proyecto web/API.

## Arquitectura

Monorepo con dos workspaces:

```
web25-991-bloques-reciclables/
  packages/
    python/           # uv workspaces
      bloque-core/
      bloque-auth/
      bloque-multitenant/
      ...
    typescript/       # pnpm + Turborepo
      bloque-ui/
      bloque-api-client/
      bloque-types/
      ...
  templates/          # Copier templates composables
  examples/           # Proyectos ejemplo
```

## Principios de Desarrollo

1. **Cada bloque es independiente.** No crear dependencias circulares entre bloques.
2. **bloque-core es el unico obligatorio.** Todo lo demas es opcional y composable.
3. **Tests en cada bloque.** Cada package tiene sus propios tests.
4. **Sin secrets.** Este repo es publico. Nunca hardcodear credenciales, API keys, o datos de clientes.
5. **Documentar con ejemplos.** Cada bloque tiene un README con ejemplo de uso.
6. **Semantic versioning.** Cada package sigue semver independientemente.

## Herramientas

| Herramienta | Proposito |
|------------|----------|
| uv (Astral) | Python package management + workspaces |
| pnpm | Node package management + workspaces |
| Turborepo | Build orchestration para packages TS |
| Copier | Living templates composables |
| Ruff | Python linter + formatter |
| Biome | TS/JS linter + formatter |
| pytest | Python tests |
| vitest | TS tests |

## Convenios

- Python: snake_case, type hints, docstrings Google style
- TypeScript: camelCase, strict mode, JSDoc donde sea necesario
- Commits: conventional commits (feat, fix, docs, chore)
- Branches: main (estable), dev (desarrollo)

## Relacion con 996

Este proyecto fue preparado por 996 (Claude Code Agentes Demo). 991 es independiente - no importa nada de 996. Los preparativos originales estan en `996/docs/991-bloques-reciclables/`.
