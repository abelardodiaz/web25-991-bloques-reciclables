# Por que Open Source

> Documento consultable. Razonamiento detras de hacer 991 publico.

---

## Razones

### 1. Los bloques no contienen secrets ni logica de negocio

Cada bloque es infraestructura generica: auth JWT, middleware RLS, cliente HTTP, componentes UI. No hay API keys, credenciales de tenants, ni logica propietaria de ningun cliente.

### 2. Cualquier developer externo podria usarlos

Un bloque como `bloque-auth-jwt` o `bloque-multitenant-rls` resuelve problemas universales. No hay razon para restringir acceso a codigo que cualquiera puede encontrar en tutoriales, pero aqui esta mejor estructurado y probado.

### 3. Contribuciones de la comunidad

Con el repo publico:
- Bug reports de developers usando los bloques en contextos que no anticipamos
- PRs con mejoras, adaptaciones a otros frameworks
- Issues que revelan edge cases

### 4. Portfolio publico de capacidad tecnica

El repo demuestra:
- Arquitectura multi-stack (Python + TypeScript)
- Patron multitenant con PostgreSQL RLS
- Monorepo bien estructurado (uv workspaces + Turborepo)
- Templates composables con Copier
- Codigo extraido de proyectos reales en produccion (031 + 048)

### 5. 996 sigue siendo privado

996 contiene:
- API keys de servicios internos (900, 99999)
- Configuracion de servidores (IPs, puertos, paths SSH)
- Preparativos con contexto de negocio de clientes
- Commands y agents con logica de orquestacion interna

Nada de eso se expone. 991 es la capa publica; 996 es la capa privada.

---

## Que NO es open source

| Publico (991) | Privado (996) |
|--------------|---------------|
| bloque-core, bloque-auth, etc. | Preparativos de proyectos |
| Templates Copier | API keys, secrets |
| Documentacion de bloques | Commands y agents internos |
| Recetas de combinacion | Config de servidores |
| CI/CD generico | Flujos de orquestacion |

---

## Licencia

MIT. Sin restricciones de uso comercial.
