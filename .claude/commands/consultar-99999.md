# Consultar Project Manager (99999)

Eres el Agente de Consultas al Project Manager (API 99999). Tu funcion es consultar el estado de proyectos,
servers, progreso, metadata, Knowledge Base (RAG) y gestionar DNS/cache/SSL via Cloudflare desde la API del Project Manager en server003:3900.

## Que es 99999 (Project Manager)

99999 es una API centralizada que monitorea todos los proyectos de la organizacion. Funciona como un dashboard programatico:
- **Proyectos**: catalogo de todos los proyectos con metadata (server, stack, version, status)
- **Status**: health checks de servers y servicios
- **Progreso**: commits y actividad de desarrollo por proyecto/fecha/rango
- **Cloudflare**: gestion de DNS, SSL, cache y analytics de dominios
- **Knowledge Base**: busqueda semantica y RAG sobre documentacion de proyectos
- **Keys**: cada proyecto tiene su propia API key con permisos configurados

## Setup (Portabilidad)

Este skill se puede replicar a cualquier proyecto. Para configurarlo:

1. **Obtener API key**: pedir al admin de 99999 una key para tu proyecto (formato: `pm-CODE-HASH`)
2. **Configurar acceso SSH**: asegurarte de tener SSH a server003 configurado
3. **Reemplazar valores** en la seccion "Conexion" abajo:
   - `YOUR_API_KEY` -> tu key real (ej: `pm-055-abc123...`)
   - `YOUR_PROJECT_CODE` -> tu codigo de proyecto (ej: `web26-055`)

> **Nota**: En el skill original de 996, la key ya esta hardcodeada. Al replicar a otro proyecto, cambiar los placeholders.

## Input del Usuario

```
$ARGUMENTS
```

**Formatos esperados:**

| Formato | Ejemplo | Accion |
|---------|---------|--------|
| `proyectos` o `listar` | `proyectos` | GET /api/projects |
| `buscar TERM` | `buscar domus` | GET /api/projects/filter/search?q=TERM |
| `proyecto ID` | `proyecto web25-031` | GET /api/projects/:id |
| `readme ID` | `readme web25-031` | GET /api/projects/:id/readme |
| `changelog ID` | `changelog 56` | GET /api/projects/:id/changelog |
| `estado` o `overview` | `estado` | GET /api/status/overview |
| `servers` | `servers` | GET /api/status/servers |
| `ping SERVER` | `ping server003` | GET /api/status/ping/:serverCode |
| `health URL` | `health http://localhost:3900` | GET /api/status/health-check?url=URL |
| `progreso` | `progreso` | GET /api/progress/today |
| `progreso FECHA` | `progreso 2026-03-01` | GET /api/progress/date/:date |
| `progreso FECHA a FECHA` | `progreso 2026-03-01 a 2026-03-05` | GET /api/progress/range?from=X&to=Y |
| `progreso proyecto ID` | `progreso proyecto 3` | GET /api/progress/project/:id |
| `proyectos activos FECHA a FECHA` | `proyectos activos 2026-03-01 a 2026-03-05` | GET /api/progress/projects-in-range |
| `grupos` | `grupos` | GET /api/projects/meta/groups |
| `conteo` | `conteo` | GET /api/projects/meta/detected-count |
| `info` | `info` | GET /api/keys/info |
| `keys help` | `keys help` | GET /api/keys/help |
| **--- Cloudflare ---** | | |
| `cf status` | `cf status` | GET /api/cloudflare/status |
| `cf zonas` | `cf zonas` | GET /api/cloudflare/zones |
| `cf zona ZONE_ID` | `cf zona c3067ed6...` | GET /api/cloudflare/zones/:zoneId |
| `cf dns ZONE_ID` | `cf dns c3067ed6...` | GET /api/cloudflare/zones/:zoneId/dns |
| `cf lookup FQDN` | `cf lookup test.redv6.com` | GET /api/cloudflare/dns/lookup?name=FQDN |
| `cf crear FQDN TYPE CONTENT` | `cf crear test.redv6.com A 10.254.0.5` | PUT /api/cloudflare/dns/upsert |
| `cf borrar FQDN` | `cf borrar test.redv6.com` | DELETE /api/cloudflare/dns/by-name?name=FQDN |
| `cf ssl ZONE_ID` | `cf ssl c3067ed6...` | GET /api/cloudflare/zones/:zoneId/ssl |
| `cf ssl ZONE_ID MODE` | `cf ssl c3067ed6... strict` | PATCH /api/cloudflare/zones/:zoneId/ssl |
| `cf purge ZONE_ID` | `cf purge c3067ed6...` | POST /api/cloudflare/zones/:zoneId/purge (purge_everything) |
| `cf purge ZONE_ID URLs` | `cf purge c3067... https://x.com/a` | POST purge con files[] |
| `cf purge ZONE_ID tags TAGS` | `cf purge c3067... tags css,js` | POST purge con tags[] |
| `cf analytics ZONE_ID` | `cf analytics c3067ed6...` | GET /api/cloudflare/zones/:zoneId/analytics |
| `cf firewall ZONE_ID` | `cf firewall c3067ed6...` | GET /api/cloudflare/zones/:zoneId/firewall |
| `cf audit` | `cf audit` | GET /api/cloudflare/audit |
| `cf help` | `cf help` | GET /api/cloudflare/help |
| **--- Knowledge Base ---** | | |
| `kb stats` | `kb stats` | GET /api/knowledge/stats |
| `kb buscar QUERY` | `kb buscar project manager` | POST /api/knowledge/search {query, top_k, project_filter} |
| `kb preguntar QUERY` | `kb preguntar que es el crm 048` | POST /api/knowledge/answer {query, top_k, provider} |
| `kb docs` | `kb docs` | GET /api/knowledge/documents |
| `kb docs PROJECT` | `kb docs web25-031` | GET /api/knowledge/documents?project_id=PROJECT |
| `kb chunks DOC_ID` | `kb chunks 5` | GET /api/knowledge/documents/:docId/chunks |
| `kb historial` | `kb historial` | GET /api/knowledge/history |
| `kb historial TICKET_ID` | `kb historial abc123` | GET /api/knowledge/history/:ticketId |
| `kb indexar` | `kb indexar` | POST /api/knowledge/index/trigger (re-indexacion manual) |
| **--- General ---** | | |
| `health` | `health` | GET /api/health (sin auth) |
| `ayuda` o `help api` | `ayuda` | GET /api/help (documentacion completa, con auth) |
| `rutas` | `rutas` | GET /api/routes (discovery de endpoints) |

## Conexion

- **Server:** server003:3900 (localhost desde server003)
- **API Key:** `pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415`
- **Acceso:** via SSH desde WSL

```bash
API_KEY="pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415"
SSH_CMD="ssh server003"
BASE_URL="http://localhost:3900"
```

## Zonas Cloudflare Conocidas

| Zona | Zone ID |
|------|---------|
| redv6.com | `c3067ed6da04554649d5af079d90c956` |
| domusrentas.com | consultar `cf zonas` |
| quierounenlace.com | consultar `cf zonas` |

## Permisos Cloudflare (cf_permissions)

La API key de 996 necesita `cf_permissions` configurado por el admin. Permisos disponibles:

| Permiso | Descripcion |
|---------|-------------|
| `dns:read` | Listar zonas y registros DNS |
| `dns:write` | Crear/editar/eliminar registros DNS |
| `cache:purge` | Purgar cache por zona, URLs o tags |
| `ssl:read` | Ver config SSL/TLS |
| `ssl:write` | Cambiar config SSL/TLS |
| `analytics:read` | Ver analytics de trafico |
| `firewall:read` | Ver reglas de firewall |

Restricciones opcionales: `allowed_subdomains` (limita dns:write), `allowed_hosts` (limita cache:purge).

## Tu Flujo de Trabajo

### 1. PARSEAR INPUT

Detecta en el input del usuario:

**Proyectos y metadata:**
- `proyectos` o `listar` -> GET /api/projects
- `buscar TERM` -> GET /api/projects/filter/search?q=TERM
- `proyecto ID` -> GET /api/projects/ID
- `readme ID` -> GET /api/projects/ID/readme
- `changelog ID` -> GET /api/projects/ID/changelog
- `grupos` -> GET /api/projects/meta/groups
- `conteo` -> GET /api/projects/meta/detected-count

**Status y servers:**
- `estado` o `overview` -> GET /api/status/overview
- `servers` -> GET /api/status/servers
- `ping SERVER` -> GET /api/status/ping/SERVER
- `health URL` -> GET /api/status/health-check?url=URL (requiere parametro URL)

**Progreso:**
- `progreso` (solo) -> GET /api/progress/today
- `progreso FECHA` -> GET /api/progress/date/FECHA
- `progreso FECHA a FECHA` -> GET /api/progress/range?from=X&to=Y
- `progreso por proyecto FECHA a FECHA` -> GET /api/progress/range-by-project?from=X&to=Y
- `progreso proyecto ID` -> GET /api/progress/project/ID
- `proyectos activos FECHA a FECHA` -> GET /api/progress/projects-in-range?from=X&to=Y

**Keys:**
- `info` -> GET /api/keys/info
- `keys help` -> GET /api/keys/help

**Cloudflare (prefijo `cf`):**
- `cf status` -> GET /api/cloudflare/status
- `cf zonas` -> GET /api/cloudflare/zones
- `cf zona ZONE_ID` -> GET /api/cloudflare/zones/ZONE_ID
- `cf dns ZONE_ID` -> GET /api/cloudflare/zones/ZONE_ID/dns
- `cf dns ZONE_ID type=A name=sub.dom.com` -> GET con query params ?type=A&name=sub.dom.com
- `cf lookup FQDN` -> GET /api/cloudflare/dns/lookup?name=FQDN (conveniencia, auto-detecta zone)
- `cf lookup FQDN TYPE` -> GET /api/cloudflare/dns/lookup?name=FQDN&type=TYPE
- `cf crear FQDN TYPE CONTENT` -> PUT /api/cloudflare/dns/upsert (conveniencia, auto-detecta zone)
- `cf crear FQDN TYPE CONTENT proxied` -> idem con proxied:true
- `cf borrar FQDN` -> DELETE /api/cloudflare/dns/by-name?name=FQDN
- `cf borrar FQDN TYPE` -> DELETE con ?name=FQDN&type=TYPE
- `cf ssl ZONE_ID` -> GET /api/cloudflare/zones/ZONE_ID/ssl
- `cf ssl ZONE_ID MODE` -> PATCH ssl con value=MODE (off|flexible|full|strict)
- `cf purge ZONE_ID` -> POST purge con purge_everything:true
- `cf purge ZONE_ID URL1 URL2...` -> POST purge con files:[URL1,URL2]
- `cf purge ZONE_ID tags TAG1,TAG2...` -> POST purge con tags:[TAG1,TAG2]
- `cf analytics ZONE_ID` -> GET /api/cloudflare/zones/ZONE_ID/analytics
- `cf analytics ZONE_ID MINS` -> GET con ?since=-MINS
- `cf firewall ZONE_ID` -> GET /api/cloudflare/zones/ZONE_ID/firewall
- `cf audit` -> GET /api/cloudflare/audit
- `cf help` -> GET /api/cloudflare/help

**Knowledge Base (prefijo `kb`):**
- `kb stats` -> GET /api/knowledge/stats
- `kb buscar QUERY` -> POST /api/knowledge/search con body {query:QUERY, top_k:5} (soporta project_filter opcional)
- `kb preguntar QUERY` -> POST /api/knowledge/answer con body {query:QUERY, top_k:5} (soporta provider opcional: deepseek, groq, gemini, grok, kimi, qwen)
- `kb docs` -> GET /api/knowledge/documents
- `kb docs PROJECT` -> GET /api/knowledge/documents?project_id=PROJECT
- `kb chunks DOC_ID` -> GET /api/knowledge/documents/DOC_ID/chunks
- `kb historial` -> GET /api/knowledge/history
- `kb historial TICKET_ID` -> GET /api/knowledge/history/TICKET_ID
- `kb indexar` -> POST /api/knowledge/index/trigger (re-indexacion manual)

**General:**
- `health` (sin args) -> GET /api/health (no requiere auth)
- `ayuda` o `help api` -> GET /api/help (documentacion completa de la API, requiere auth)
- `rutas` -> GET /api/routes (discovery de endpoints)

### 2. EJECUTAR CONSULTA

Construye y ejecuta el comando SSH + curl:

```bash
wsl bash -c 'ssh server003 "curl -s -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" http://localhost:3900/ENDPOINT"'
```

**Ejemplos concretos - Proyectos/Status/Progreso:**

#### Listar proyectos
```bash
wsl bash -c 'ssh server003 "curl -s -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" http://localhost:3900/api/projects"'
```

#### Buscar proyectos
```bash
wsl bash -c 'ssh server003 "curl -s -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" \"http://localhost:3900/api/projects/filter/search?q=TERM\""'
```

#### Detalle de proyecto
```bash
wsl bash -c 'ssh server003 "curl -s -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" http://localhost:3900/api/projects/ID"'
```

#### Estado general
```bash
wsl bash -c 'ssh server003 "curl -s -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" http://localhost:3900/api/status/overview"'
```

#### Servers
```bash
wsl bash -c 'ssh server003 "curl -s -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" http://localhost:3900/api/status/servers"'
```

#### Ping a server
```bash
wsl bash -c 'ssh server003 "curl -s -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" http://localhost:3900/api/status/ping/SERVER_CODE"'
```

#### Health check (requiere URL)
```bash
wsl bash -c 'ssh server003 "curl -s -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" \"http://localhost:3900/api/status/health-check?url=http://localhost:3900\""'
```

#### Progreso de hoy
```bash
wsl bash -c 'ssh server003 "curl -s -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" http://localhost:3900/api/progress/today"'
```

#### Progreso por fecha
```bash
wsl bash -c 'ssh server003 "curl -s -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" http://localhost:3900/api/progress/date/FECHA"'
```

#### Progreso en rango
```bash
wsl bash -c 'ssh server003 "curl -s -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" \"http://localhost:3900/api/progress/range?from=FECHA1&to=FECHA2\""'
```

#### Progreso por proyecto en rango (con insertions/deletions/daysActive)
```bash
wsl bash -c 'ssh server003 "curl -s -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" \"http://localhost:3900/api/progress/range-by-project?from=FECHA1&to=FECHA2\""'
```

#### Progreso de un proyecto
```bash
wsl bash -c 'ssh server003 "curl -s -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" http://localhost:3900/api/progress/project/ID"'
```

**Ejemplos concretos - Cloudflare:**

#### CF: Status
```bash
wsl bash -c 'ssh server003 "curl -s -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" http://localhost:3900/api/cloudflare/status"'
```

#### CF: Listar zonas
```bash
wsl bash -c 'ssh server003 "curl -s -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" http://localhost:3900/api/cloudflare/zones"'
```

#### CF: DNS records de una zona
```bash
wsl bash -c 'ssh server003 "curl -s -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" http://localhost:3900/api/cloudflare/zones/ZONE_ID/dns"'
```

#### CF: Lookup DNS (conveniencia - sin zone_id)
```bash
wsl bash -c 'ssh server003 "curl -s -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" \"http://localhost:3900/api/cloudflare/dns/lookup?name=FQDN&type=A\""'
```

#### CF: Upsert DNS (conveniencia - crear o actualizar)
```bash
wsl bash -c 'ssh server003 "curl -s -X PUT -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" -H \"Content-Type: application/json\" http://localhost:3900/api/cloudflare/dns/upsert -d '"'"'{\"name\":\"FQDN\",\"type\":\"A\",\"content\":\"IP\",\"proxied\":true}'"'"'"'
```

#### CF: Borrar DNS por nombre (conveniencia)
```bash
wsl bash -c 'ssh server003 "curl -s -X DELETE -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" \"http://localhost:3900/api/cloudflare/dns/by-name?name=FQDN&type=A\""'
```

#### CF: Crear DNS record (con zone_id)
```bash
wsl bash -c 'ssh server003 "curl -s -X POST -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" -H \"Content-Type: application/json\" http://localhost:3900/api/cloudflare/zones/ZONE_ID/dns -d '"'"'{\"type\":\"A\",\"name\":\"FQDN\",\"content\":\"IP\",\"proxied\":true}'"'"'"'
```

#### CF: Editar DNS record
```bash
wsl bash -c 'ssh server003 "curl -s -X PUT -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" -H \"Content-Type: application/json\" http://localhost:3900/api/cloudflare/zones/ZONE_ID/dns/RECORD_ID -d '"'"'{\"content\":\"NEW_IP\"}'"'"'"'
```

#### CF: Eliminar DNS record
```bash
wsl bash -c 'ssh server003 "curl -s -X DELETE -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" http://localhost:3900/api/cloudflare/zones/ZONE_ID/dns/RECORD_ID"'
```

#### CF: Ver SSL
```bash
wsl bash -c 'ssh server003 "curl -s -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" http://localhost:3900/api/cloudflare/zones/ZONE_ID/ssl"'
```

#### CF: Cambiar SSL mode
```bash
wsl bash -c 'ssh server003 "curl -s -X PATCH -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" -H \"Content-Type: application/json\" http://localhost:3900/api/cloudflare/zones/ZONE_ID/ssl -d '"'"'{\"value\":\"strict\"}'"'"'"'
```

#### CF: Purgar cache (todo)
```bash
wsl bash -c 'ssh server003 "curl -s -X POST -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" -H \"Content-Type: application/json\" http://localhost:3900/api/cloudflare/zones/ZONE_ID/purge -d '"'"'{\"purge_everything\":true}'"'"'"'
```

#### CF: Purgar cache (URLs especificas, max 30)
```bash
wsl bash -c 'ssh server003 "curl -s -X POST -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" -H \"Content-Type: application/json\" http://localhost:3900/api/cloudflare/zones/ZONE_ID/purge -d '"'"'{\"files\":[\"URL1\",\"URL2\"]}'"'"'"'
```

#### CF: Purgar cache (por tags)
```bash
wsl bash -c 'ssh server003 "curl -s -X POST -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" -H \"Content-Type: application/json\" http://localhost:3900/api/cloudflare/zones/ZONE_ID/purge -d '"'"'{\"tags\":[\"css\",\"js\"]}'"'"'"'
```

#### CF: Analytics
```bash
wsl bash -c 'ssh server003 "curl -s -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" \"http://localhost:3900/api/cloudflare/zones/ZONE_ID/analytics?since=-1440\""'
```

#### CF: Firewall rules
```bash
wsl bash -c 'ssh server003 "curl -s -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" http://localhost:3900/api/cloudflare/zones/ZONE_ID/firewall"'
```

#### CF: Audit log
```bash
wsl bash -c 'ssh server003 "curl -s -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" http://localhost:3900/api/cloudflare/audit"'
```

#### CF: Help
```bash
wsl bash -c 'ssh server003 "curl -s -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" http://localhost:3900/api/cloudflare/help"'
```

**Ejemplos concretos - Knowledge Base:**

#### KB: Stats
```bash
wsl bash -c 'ssh server003 "curl -s -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" http://localhost:3900/api/knowledge/stats"'
```

#### KB: Busqueda semantica (POST)
```bash
wsl bash -c 'ssh server003 "curl -s -X POST -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" -H \"Content-Type: application/json\" http://localhost:3900/api/knowledge/search -d '"'"'{\"query\":\"QUERY\",\"top_k\":5}'"'"'"'
```

#### KB: Busqueda semantica con project_filter (POST)
```bash
wsl bash -c 'ssh server003 "curl -s -X POST -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" -H \"Content-Type: application/json\" http://localhost:3900/api/knowledge/search -d '"'"'{\"query\":\"QUERY\",\"top_k\":5,\"project_filter\":\"PROJECT_ID\"}'"'"'"'
```

#### KB: Pregunta RAG (POST)
```bash
wsl bash -c 'ssh server003 "curl -s -X POST -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" -H \"Content-Type: application/json\" http://localhost:3900/api/knowledge/answer -d '"'"'{\"query\":\"QUERY\",\"top_k\":5}'"'"'"'
```

#### KB: Pregunta RAG con provider (POST)
```bash
wsl bash -c 'ssh server003 "curl -s -X POST -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" -H \"Content-Type: application/json\" http://localhost:3900/api/knowledge/answer -d '"'"'{\"query\":\"QUERY\",\"top_k\":5,\"provider\":\"PROVIDER\"}'"'"'"'
```

#### KB: Re-indexacion manual (POST)
```bash
wsl bash -c 'ssh server003 "curl -s -X POST -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" http://localhost:3900/api/knowledge/index/trigger"'
```

#### KB: Listar documentos
```bash
wsl bash -c 'ssh server003 "curl -s -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" http://localhost:3900/api/knowledge/documents"'
```

#### KB: Documentos por proyecto
```bash
wsl bash -c 'ssh server003 "curl -s -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" \"http://localhost:3900/api/knowledge/documents?project_id=PROJECT\""'
```

#### KB: Chunks de un documento
```bash
wsl bash -c 'ssh server003 "curl -s -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" http://localhost:3900/api/knowledge/documents/DOC_ID/chunks"'
```

#### KB: Historial de consultas
```bash
wsl bash -c 'ssh server003 "curl -s -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" http://localhost:3900/api/knowledge/history"'
```

#### KB: Detalle de consulta
```bash
wsl bash -c 'ssh server003 "curl -s -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" http://localhost:3900/api/knowledge/history/TICKET_ID"'
```

**Ejemplos concretos - General:**

#### Health (sin auth)
```bash
wsl bash -c 'ssh server003 "curl -s http://localhost:3900/api/health"'
```

#### Ayuda / Help API (documentacion completa)
```bash
wsl bash -c 'ssh server003 "curl -s -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" http://localhost:3900/api/help"'
```

#### Rutas (discovery de endpoints)
```bash
wsl bash -c 'ssh server003 "curl -s -H \"X-API-Key: pm-996-e5a335be82ff2799353a6a865d4ae3f23bbd16c901d81415\" http://localhost:3900/api/routes"'
```

### 3. PRESENTAR RESULTADO

Parsea el JSON y presenta en formato legible:

**Para lista de proyectos:**

```
PROJECT MANAGER - PROYECTOS

| # | Code | Nombre | Server | Status | Version |
|---|------|--------|--------|--------|---------|
| 1 | web25-031 | Domus | server005 | online | 3.2.1 |
| ... | ... | ... | ... | ... | ... |

Total: X proyectos
```

**Para status overview:**

```
PROJECT MANAGER - ESTADO GENERAL

Total: X proyectos
Online: X | Offline: X
Dev: X | Prod: X
```

**Para servers:**

```
PROJECT MANAGER - SERVERS

| Server | Proyectos | Estado |
|--------|-----------|--------|
| server003 | 12 | online |
| server005 | 8 | online |
```

**Para health-check:**

```
PROJECT MANAGER - HEALTH CHECK

URL: http://localhost:3900
Status: [status code]
Response Time: [responseTime]ms
Success: [true/false]
```

**Para progreso:**

```
PROJECT MANAGER - PROGRESO [FECHA]

| Proyecto | Commits | Ultimo commit |
|----------|---------|---------------|
| web25-031 | 5 | feat: nueva feature |
```

**Para progreso por proyecto en rango (range-by-project):**

```
PROJECT MANAGER - PROGRESO POR PROYECTO [FECHA1 a FECHA2]

| Proyecto | Commits | +Insertions | -Deletions | Dias activos |
|----------|---------|-------------|------------|--------------|
| web25-031 | 12 | +450 | -120 | 3 |
| web25-044 | 5 | +200 | -50 | 2 |

Total: X proyectos activos
```

**Para detalle de proyecto:**

```
PROJECT MANAGER - PROYECTO [CODE]

Nombre: [name]
Code: [code]
Server: [server]
Status: [status]
Version: [version]
Path: [path]
Descripcion: [description]
```

**Para CF zonas:**

```
CLOUDFLARE - ZONAS

| Zona | ID | Status | Plan |
|------|----|--------|------|
| redv6.com | c3067ed6... | active | free |
| domusrentas.com | abc123... | active | pro |

Total: X zonas
```

**Para CF DNS records:**

```
CLOUDFLARE - DNS [zona]

| Type | Name | Content | Proxied | TTL |
|------|------|---------|---------|-----|
| A | test.redv6.com | 10.254.0.5 | yes | auto |
| CNAME | www.redv6.com | redv6.com | yes | auto |

Total: X records
```

**Para CF lookup:**

```
CLOUDFLARE - LOOKUP [fqdn]

Found: yes/no
Zone: redv6.com (c3067ed6...)
Record: A test.redv6.com -> 10.254.0.5 (proxied, ttl=auto)
```

**Para CF upsert/crear:**

```
CLOUDFLARE - DNS [action: created/updated]

Zone: redv6.com
Record: A test.redv6.com -> 10.254.0.5 (proxied)
```

**Para CF SSL:**

```
CLOUDFLARE - SSL [zona]

Mode: strict
Always HTTPS: on
```

**Para CF analytics:**

```
CLOUDFLARE - ANALYTICS [zona] (ultimas 24h)

Requests: X total | X cached | X uncached
Bandwidth: X MB total | X MB cached
Threats: X blocked
```

**Para KB stats:**

```
KNOWLEDGE BASE - STATS

Total documentos: X
Total chunks: X
Por proyecto:
| Proyecto | Docs | Chunks |
|----------|------|--------|
| web25-031 | 5 | 120 |
Jobs recientes: X
```

**Para KB search:**

```
KNOWLEDGE BASE - BUSQUEDA: "QUERY"

| # | Score | Documento | Fragmento |
|---|-------|-----------|-----------|
| 1 | 0.92 | README web25-031 | ...texto relevante... |
| 2 | 0.85 | CHANGELOG web25-044 | ...texto relevante... |

Total: X resultados
```

**Para KB answer (RAG):**

```
KNOWLEDGE BASE - RESPUESTA RAG

Pregunta: QUERY

Respuesta:
[respuesta generada por el modelo]

Fuentes:
- [doc_id] documento_nombre (score: 0.92)
- [doc_id] documento_nombre (score: 0.85)
```

**Para KB docs:**

```
KNOWLEDGE BASE - DOCUMENTOS

| ID | Proyecto | Tipo | Nombre | Chunks | Fecha |
|----|----------|------|--------|--------|-------|
| 1 | web25-031 | readme | README.md | 24 | 2026-03-10 |

Total: X documentos
```

**Para KB chunks:**

```
KNOWLEDGE BASE - CHUNKS [doc_id]

| # | Chunk ID | Contenido (preview) |
|---|----------|---------------------|
| 1 | 101 | Primer parrafo del documento... |
| 2 | 102 | Segundo parrafo... |

Total: X chunks
```

**Para KB historial:**

```
KNOWLEDGE BASE - HISTORIAL

| Ticket | Tipo | Query | Resultados | Fecha |
|--------|------|-------|------------|-------|
| abc123 | search | project manager | 5 | 2026-03-15 |

Total: X consultas
```

**Para help API (ayuda):**

```
API 99999 - DOCUMENTACION COMPLETA

Modulos disponibles:
- Projects: X endpoints
- Status: X endpoints
- Progress: X endpoints
- Cloudflare: X endpoints
- Knowledge: X endpoints
- Keys: X endpoints
- Docs: X endpoints

[resumen de endpoints por modulo]
```

**Para rutas:**

```
API 99999 - RUTAS

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | /api/health | Health check |
| GET | /api/projects | Lista proyectos |
| ... | ... | ... |

Total: X rutas
```

**Para kb indexar:**

```
KNOWLEDGE BASE - RE-INDEXACION

Trigger: enviado
[mensaje de respuesta de la API]
```

**Para health:**

```
API 99999 - HEALTH

Status: ok
Version: [version]
Timestamp: [timestamp]
```

### 4. MANEJO DE ERRORES

| Error | Causa | Solucion |
|-------|-------|----------|
| Connection refused | API 99999 no corre | Verificar: `ssh server003 'curl -s http://localhost:3900/api/health'` |
| 401 Unauthorized | API key invalida | Verificar key en MEMORY.md |
| 403 Forbidden (CF) | Falta cf_permissions en la key | Pedir al admin que configure cf_permissions |
| 404 Not Found | Proyecto/endpoint/zone no existe | Verificar ID o endpoint |
| SSH timeout | Problema de red/VPN | Verificar conectividad SSH |

## Ejemplos de Uso

```
/consultar-99999 proyectos
/consultar-99999 buscar domus
/consultar-99999 proyecto web25-031
/consultar-99999 readme web25-031
/consultar-99999 estado
/consultar-99999 servers
/consultar-99999 ping server003
/consultar-99999 health http://localhost:3900
/consultar-99999 progreso
/consultar-99999 progreso 2026-03-01
/consultar-99999 progreso 2026-03-01 a 2026-03-05
/consultar-99999 progreso por proyecto 2026-03-01 a 2026-03-05
/consultar-99999 progreso proyecto 3
/consultar-99999 grupos
/consultar-99999 keys help
/consultar-99999 ayuda
/consultar-99999 rutas
/consultar-99999 cf status
/consultar-99999 cf zonas
/consultar-99999 cf dns c3067ed6da04554649d5af079d90c956
/consultar-99999 cf lookup test.redv6.com
/consultar-99999 cf lookup test.redv6.com A
/consultar-99999 cf crear test.redv6.com A 10.254.0.5 proxied
/consultar-99999 cf borrar test.redv6.com A
/consultar-99999 cf ssl c3067ed6da04554649d5af079d90c956
/consultar-99999 cf ssl c3067ed6da04554649d5af079d90c956 strict
/consultar-99999 cf purge c3067ed6da04554649d5af079d90c956
/consultar-99999 cf analytics c3067ed6da04554649d5af079d90c956
/consultar-99999 cf firewall c3067ed6da04554649d5af079d90c956
/consultar-99999 cf purge c3067ed6da04554649d5af079d90c956 tags css,js
/consultar-99999 cf audit
/consultar-99999 cf help
/consultar-99999 kb stats
/consultar-99999 kb buscar project manager
/consultar-99999 kb buscar api rest endpoints
/consultar-99999 kb buscar crm project web25-048
/consultar-99999 kb preguntar que es el crm 048
/consultar-99999 kb preguntar que stacks usamos provider groq
/consultar-99999 kb preguntar como funciona el deploy de 031
/consultar-99999 kb indexar
/consultar-99999 kb docs
/consultar-99999 kb docs web25-031
/consultar-99999 kb chunks 5
/consultar-99999 kb historial
/consultar-99999 kb historial abc123
/consultar-99999 health
```

## Notas

- API 99999 esta en server003:3900 (tambien accesible via VPN: `http://10.254.0.3:3900`)
- Lectura de proyectos/status/progreso funciona con la key actual
- `GET /api/health` no requiere auth - retorna `{status, timestamp, version}` - util para verificar si la API esta corriendo
- `health-check` requiere parametro `?url=URL` - retorna `{status, responseTime, success}`
- `range-by-project` retorna campos enriquecidos: `totalCommits`, `totalInsertions`, `totalDeletions`, `daysActive`
- Cloudflare requiere `cf_permissions` configurado en la key por el admin
- CF purge soporta 3 modos: `purge_everything:true`, `files:[URLs]` (max 30), o `tags:[tags]` (cache tags)
- CF DNS create/upsert acepta `ttl` y `priority` opcionales ademas de name/type/content/proxied
- Endpoints de conveniencia (`/dns/lookup`, `/dns/upsert`, `/dns/by-name`) auto-detectan zone_id
- Zone ID de redv6.com: `c3067ed6da04554649d5af079d90c956`
- La key de 996 esta hardcodeada en este skill. Para replicar a otro proyecto, ver seccion "Setup (Portabilidad)"
- Acceso siempre via `wsl bash -c 'ssh server003 ...'` desde Windows/PowerShell
- SSL modes: off, flexible, full, strict
- Knowledge Base: `kb buscar` y `kb preguntar` son POST con body JSON `{query, top_k}`. Los demas endpoints KB son GET
- `GET /api/help` retorna documentacion completa de todos los modulos de la API (requiere auth)
- `GET /api/routes` retorna lista de todos los endpoints disponibles (requiere auth)
- `POST /api/knowledge/index/trigger` dispara re-indexacion manual de la Knowledge Base
- `kb buscar` soporta `project_filter` opcional para filtrar resultados por project_id
- `kb preguntar` soporta `provider` opcional: deepseek (default), groq, gemini, grok, kimi, qwen
- Auto top_k: si no se especifica top_k, la API clasifica automaticamente: specific=10, default=15, broad=25
- Endpoints que NO existen: `/api/status` (solo), `/api/projects/filter/active`, `/api/projects/filter/by-server/:code`, `/api/projects/filter/by-stack/:stack`, `/api/projects/filter/by-group/:id`, `/api/knowledge/reindex`, `/api/knowledge/chunks/:id`
