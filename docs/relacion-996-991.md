# Relacion 996 - 991

> Documento consultable. Como interactuan ambos proyectos.

---

## Diagrama de Flujo

```
                    FLUJO GREENFIELD (proyecto nuevo)
                    =================================

  [Usuario]
     |
     | "Crea proyecto SaaS multitenant"
     v
  [Claude 996]
     |
     | 1. Lee preparativos en docs/
     | 2. Genera PROMPT-ARRANQUE
     | 3. Referencia bloques de 991
     v
  [PROMPT-ARRANQUE.md]
     |
     | Instrucciones:
     |   - uv add bloque-core bloque-auth bloque-multitenant
     |   - pnpm add @bloque/ui @bloque/api-client
     |   - copier copy template-base .
     v
  [Proyecto Hijo (ej: web25-070)]
     |
     | Instala bloques desde 991
     v
  [991 - Bloques Reciclables]
     |
     | Provee packages versionados
     | (PyPI + npm registry)
     |
     +-- bloque-core (obligatorio)
     +-- bloque-auth (si necesita login)
     +-- bloque-multitenant (si necesita tenants)
     +-- bloque-ui (si tiene frontend)
     +-- ... (composable)
```

---

## Flujo Brownfield (proyecto existente)

```
  [Proyecto existente]
     |
     | "Necesito multitenant"
     v
  [Developer]
     |
     | uv add bloque-multitenant-rls
     | (no necesita 996, instala directo)
     v
  [991 - Bloques Reciclables]
     |
     | Provee solo el bloque necesario
     +-- bloque-multitenant-rls
```

---

## Puntos de Contacto

| Momento | 996 hace | 991 provee |
|---------|----------|-----------|
| Preparativos | Lista bloques recomendados en PROMPT-ARRANQUE | Nada (pasivo) |
| Arranque proyecto | Genera scaffolding con referencias a bloques | Packages + templates Copier |
| Desarrollo | No interviene | Bloques instalados como dependencias |
| Nuevo bloque | Documenta en preparativos futuros | Publica nueva version |

---

## Independencia

991 **no depende** de 996. Cualquier developer puede:
1. Clonar 991
2. Leer el catalogo de bloques
3. Instalar lo que necesite
4. Sin saber que 996 existe

996 **referencia** a 991 en sus preparativos, pero 991 nunca importa nada de 996.

---

## Evolucion

```
Hoy:
  996 prepara -> proyecto hijo instala bloques de 991

Futuro:
  991 evoluciona independiente
  Nuevos bloques se crean por demanda
  Comunidad contribuye bloques
  996 actualiza preparativos para referenciar nuevos bloques
```
