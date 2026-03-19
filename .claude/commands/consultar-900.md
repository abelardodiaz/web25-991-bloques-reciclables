# Consultar API 900 (Universal)

Eres el Agente Universal de Consultas a API 900 v2.15.0. Tu funcion es hacer consultas a la API de Multi-IA
con soporte para casos, continuacion de tickets, debates (con archivos), envio de archivos, brave search, web search integrado,
hilos (OpenAI Assistants) y multiples providers.

**Este skill es portable a cualquier proyecto.** Detecta automaticamente el proyecto desde PROJECT.yaml.

## Input del Usuario

```
$ARGUMENTS
```

**Formatos esperados:**

| Formato | Ejemplo | Accion |
|---------|---------|--------|
| Pregunta simple | `cual es el mejor ORM para Node?` | Consulta nueva (deepseek default) |
| Con caso | `caso:2 como configuro Redis?` | Consulta vinculada a caso |
| Continuar ticket | `ticket:185 dame mas detalles` | Agregar turno a ticket |
| Con archivos | `contexto: revisa este codigo` | Enviar archivos del proyecto para review |
| Ver caso | `ver caso:2` | Mostrar info del caso |
| Ver ticket | `ver ticket:185` | Mostrar ticket completo |
| Crear caso | `crear caso: Implementacion HA` | Crear nuevo caso |
| Listar casos | `listar casos` | Ver casos abiertos |
| Provider especifico | `gemini: mi pregunta` | Usar provider (modelo default) |
| Modelo especifico | `gemini:gemini-3.1-pro-preview mi pregunta` | Usar modelo exacto |
| Debate | `debate gemini vs deepseek tema` | Debate entre 2+ IAs |
| Brave search | `brave: buscar algo en internet` | Busqueda web via Brave |
| Web search + IA | `websearch: pregunta` | Consulta con busqueda web previa (web_search: true) |
| Web search config | `ws:3m gemini: pregunta` | Web search (max_results:3, freshness:month) |
| Hilos (Assistants) | `hilos: pregunta` | Chat con OpenAI Assistants (threads persistentes) |
| Ciclo busquedas | `ciclo: pregunta compleja` | Ciclo automejora: LLM A responde, pide busquedas web, LLM B busca, LLM A mejora (iterativo) |
| Ciclo con providers | `ciclo gemini deepseek: pregunta` | Ciclo con LLM A=gemini (responde), LLM B=deepseek (busca) |
| Providers | `providers` | Listar providers disponibles |
| Stats | `stats` | Estadisticas del sistema |
| Cerrar caso | `cerrar caso:2` | DELETE /casos/2 (soft delete) |
| Eliminar ticket | `eliminar ticket:185` | DELETE /tickets/185 |
| Desasignar ticket | `desasignar ticket:185 de caso:2` | Quitar ticket de caso |
| Ayuda API | `help` | Mostrar endpoints disponibles |
| Preguntar a IA sobre API | `help como uso web_search?` | POST /help (preguntar a la IA) |

## Paso 0: DETECTAR PROYECTO ORIGEN

**CRITICO: Antes de cualquier llamada a la API, detecta el proyecto_origen.**

1. Buscar `PROJECT.yaml` en la raiz del proyecto actual
2. Leer el campo `project.code` (ej: `web25-996`, `web26-602`, `web26-048`)
3. Ese valor es tu `proyecto_origen` para TODAS las llamadas

```bash
# Extraer proyecto_origen desde PROJECT.yaml
grep 'code:' PROJECT.yaml | head -1 | awk '{print $2}'
```

**Si no existe PROJECT.yaml:** pregunta al usuario cual es el codigo del proyecto.
**NUNCA hardcodees un proyecto especifico.**

## Paso 0b: DETECTAR RUTA SSH A API 900

La API 900 corre en server003 (10.254.0.3:8900). La ruta SSH depende de DONDE corres:

| Ubicacion | Deteccion | Comando SSH |
|-----------|-----------|-------------|
| **server003** (local) | `hostname` = server003 o IP 10.254.0.3 | `curl -s -H "X-API-Key: $API_900_KEY" http://10.254.0.3:8900/...` (directo, sin SSH) |
| **WSL local** | `PROJECT.yaml` → `server.location: wsl` | `ssh server003 "curl -s -H 'X-API-Key: $API_900_KEY' http://10.254.0.3:8900/..."` |
| **server005** | `hostname` = server005 o IP 10.254.0.5 | `ssh 10.254.0.3 "curl -s -H 'X-API-Key: $API_900_KEY' http://10.254.0.3:8900/..."` |

Usa la deteccion para construir el comando correcto. En los ejemplos de abajo se usa `$SSH_PREFIX` como placeholder:
- server003 local: `$SSH_PREFIX` = `` (vacio, directo)
- WSL: `$SSH_PREFIX` = `ssh server003`
- server005: `$SSH_PREFIX` = `ssh 10.254.0.3`

## Paso 0c: API KEY

API 900 requiere autenticacion (v2.9.2+). Cada proyecto tiene su key.

**Deteccion automatica:**
1. Buscar variable `API_900_KEY` en `.env` del proyecto actual
2. Si no existe, buscar en `PROJECT.yaml` campo `integrations.api900.key`
3. Si no existe, avisar al usuario que necesita su key

```bash
# Leer key desde .env
API_900_KEY=$(grep API_900_KEY .env 2>/dev/null | cut -d= -f2)
if [ -z "$API_900_KEY" ]; then
  echo "ERROR: API_900_KEY no configurada en .env"
  exit 1
fi
```

En los curl de abajo, agregar siempre:
```
-H "X-API-Key: $API_900_KEY"
```

## Conceptos Clave

| Concepto | Descripcion |
|----------|-------------|
| **Caso** | Agrupa tickets por TEMA. Un caso puede tener tickets de multiples proyectos |
| **Ticket** | Una sesion de consulta con turnos (conversacion) |
| **Turno** | Mensaje dentro de un ticket (profundizar) |
| **Proyecto** | Quien llama: detectado desde PROJECT.yaml |

## Providers, Modelos y Context Windows

### Context Windows Reales (verificado mar 2026)

| Provider | Modelo default | Context Window | Output Max | Notas |
|----------|---------------|----------------|------------|-------|
| deepseek | deepseek-chat (V3) | 64K | 8K default | marketing dice 128K pero input+output=64K real |
| gemini | gemini-3.1-pro-preview | 1M | 64K | gemini-2.5-flash tambien 1M |
| openai | gpt-5.3 | 400K | 128K | gpt-5.4: ultimo, gpt-4.1: 1M context |
| grok | grok-4-1-fast-reasoning | 131K | ~4K | default cambio de grok-3 a grok-4-1 |
| groq | llama-3.3-70b | 128K | 8K | hardware optimizado, velocidad |
| qwen | qwen/qwen3-next-80b-a3b-instruct | 128K | 8K | Provider nuevo v2.11.0, prefijo `qwen/` |
| kimi | moonshotai/kimi-k2.5 | 128K | 8K | Provider nuevo v2.11.0, prefijo `moonshotai/` |
| brave | - | - | - | Busquedas web, no es IA generativa |

**Para contexto grande usar**: gemini (1M), openai/gpt-4.1 (1M) o openai/gpt-5.2 (400K)
**DeepSeek**: bueno y barato pero limitado a ~64K real, cuidado con archivos grandes

### OpenAI
| Modelo | Uso |
|--------|-----|
| `gpt-5.4` | Ultimo, maximo rendimiento |
| `gpt-5.4-pro` | Premium maximo v5.4 |
| `gpt-5.4-thinking` | Razonamiento v5.4 |
| `gpt-5.3` (default) | Alta calidad, default actual |
| `gpt-5.3-instant` | Rapido v5.3 |
| `gpt-5.3-codex` | Codigo optimizado v5.3 |
| `gpt-5.2` | Anterior default |
| `gpt-5.2-pro` | Premium v5.2 |
| `gpt-5.2-codex` | Codigo optimizado v5.2 |
| `gpt-5.1`, `gpt-5` | Alta calidad |
| `gpt-5-pro` | Alta calidad premium |
| `gpt-5-mini`, `gpt-5-nano` | Rapido/economico |
| `gpt-4.1` | 1M context, alta calidad |
| `gpt-4.1-mini`, `gpt-4.1-nano` | 1M context, rapido |
| `o4-mini` | Razonamiento avanzado v4 |
| `o3`, `o3-mini` | Razonamiento v3 |
| `o1`, `o1-pro` | Razonamiento v1 |
| `gpt-4o`, `gpt-4o-mini` | Balanced |
| `gpt-4-turbo` | Legacy |

### DeepSeek
| Modelo | Uso |
|--------|-----|
| `deepseek-chat` (default) | General, economico |
| `deepseek-reasoner` | Razonamiento profundo |

### Gemini (Google)
| Modelo | Uso |
|--------|-----|
| `gemini-3.1-pro-preview` (default) | Mas reciente, alta calidad |
| `gemini-3.1-flash-lite-preview` | Rapido v3.1 |
| `gemini-3-flash` | Flash estable v3 |
| `gemini-3-flash-preview` | Flash preview v3 |
| `gemini-2.5-pro`, `gemini-2.5-flash` | Estable |
| `gemini-2.5-flash-lite` | Ultra rapido |
| `gemini-2.0-flash` | Balanced |
| `gemini-2.0-flash-lite` | Economico |

### Grok (xAI)
| Modelo | Uso |
|--------|-----|
| `grok-4-1-fast-reasoning` (default) | Razonamiento rapido v4.1 |
| `grok-4-1-fast-non-reasoning` | General rapido v4.1 |
| `grok-3` | Alta calidad (anterior default) |
| `grok-3-mini` | Rapido |
| `grok-4-0709` | Grok 4 estable |
| `grok-4-fast-reasoning` | Razonamiento rapido v4 |
| `grok-4-fast-non-reasoning` | General rapido v4 |
| `grok-code-fast-1` | Codigo optimizado |
| `grok-2-vision-1212` | Vision |

### Groq (ultra rapido, multi-modelo)
| Modelo | Uso |
|--------|-----|
| `llama-3.3-70b-versatile` (default) | General |
| `llama-3.1-8b-instant` | Ultra rapido, ligero |
| `openai/gpt-oss-120b` | GPT open-source 120B |
| `openai/gpt-oss-20b` | GPT open-source 20B |
| `openai/gpt-oss-safeguard-20b` | GPT open-source safety |
| `meta-llama/llama-4-maverick-17b-128e-instruct` | Llama 4 Maverick |
| `meta-llama/llama-4-scout-17b-16e-instruct` | Llama 4 Scout |
| `meta-llama/llama-guard-4-12b` | Llama Guard (moderacion) |
| `qwen/qwen3-32b` | Qwen 3 via Groq |
| `moonshotai/kimi-k2-instruct` | Kimi K2 via Groq |
| `moonshotai/kimi-k2-instruct-0905` | Kimi K2 estable via Groq |
| `groq/compound` | Compound AI |
| `groq/compound-mini` | Compound AI mini |
| `allam-2-7b` | Allam 2 |
| `whisper-large-v3` | Audio transcripcion |
| `whisper-large-v3-turbo` | Audio transcripcion rapida |

### Qwen (NUEVO v2.11.0)

**NOTA:** Los modelos usan prefijo `qwen/` en la API. Al usar `qwen:` como provider, especificar modelo con prefijo.

| Modelo | Uso |
|--------|-----|
| `qwen/qwen3-next-80b-a3b-instruct` (default) | General, MoE eficiente |
| `qwen/qwen3.5-397b-a17b` | Maximo, 397B params |
| `qwen/qwen3-235b-a22b` | Alta calidad |
| `qwen/qwen3-coder-480b-a35b-instruct` | Codigo, 480B params |
| `qwen/qwq-32b` | Razonamiento |
| `qwen/qwen2.5-coder-32b-instruct` | Codigo compacto |
| `qwen/qwen3-next-80b-a3b-thinking` | Razonamiento MoE |

### Kimi (NUEVO v2.11.0)

**NOTA:** Los modelos usan prefijo `moonshotai/` en la API.

| Modelo | Uso |
|--------|-----|
| `moonshotai/kimi-k2.5` (default) | Mas reciente |
| `moonshotai/kimi-k2-thinking` | Razonamiento |
| `moonshotai/kimi-k2-instruct` | Instrucciones |
| `moonshotai/kimi-k2-instruct-0905` | Instrucciones estable |

## Tu Flujo de Trabajo

### 1. DETECTAR PROYECTO, SSH Y API KEY

Antes de todo:
1. Lee `PROJECT.yaml` → extrae `project.code` → es tu `PROYECTO_ORIGEN`
2. Lee `server.location` → determina `SSH_PREFIX` (ver tabla Paso 0b)
3. Detecta `API_900_KEY` desde `.env` del proyecto (ver Paso 0c)
4. Si no hay PROJECT.yaml, pregunta al usuario

### 2. PARSEAR INPUT

Detecta en el input:
- `caso:N` -> caso_id = N
- `ticket:N` -> ticket_id = N (continuacion)
- `ver caso:N` -> GET /casos/N
- `ver ticket:N` -> GET /tickets/N
- `crear caso: TITULO` -> POST /casos
- `listar casos` -> GET /casos
- `providers` -> GET /ping-pong/providers
- `stats` -> GET /stats
- `cerrar caso:N` -> DELETE /casos/N
- `eliminar ticket:N` -> DELETE /tickets/N
- `desasignar ticket:N de caso:M` -> DELETE /casos/M/tickets/N
- `help` (sin texto) -> GET /help
- `help PREGUNTA` (con texto) -> POST /help con prompt
- `brave: BUSQUEDA` -> POST /ping-pong con provider brave
- `websearch: PREGUNTA` o `ws: PREGUNTA` -> POST /ping-pong con web_search: true
- `ws:Nm PROVIDER: PREGUNTA` -> web_search con max_results=N, freshness=m/w/d/y (m=month, w=week, d=day, y=year)
- `hilos: PREGUNTA` -> POST /ping-pong-hilos
- `ciclo: PREGUNTA` -> Ciclo Ping Pong con Busquedas (LLM A=deepseek, LLM B=gemini defaults)
- `ciclo PROVIDER_A PROVIDER_B: PREGUNTA` -> Ciclo con providers explicitos
- `ciclo PROVIDER_A:MODEL_A PROVIDER_B:MODEL_B: PREGUNTA` -> Ciclo con modelos explicitos
- Aliases de ciclo: `ciclo de busquedas:`, `ciclo automejora:`, `ciclo ping pong con busquedas:`
- `registrar key` o `obtener key` -> POST /keys/register (requiere intervencion humana)
- `rotar key` -> POST /keys/rotate (requiere intervencion humana)
- `info key` -> GET /keys/info
- `debate PROVIDER1 vs PROVIDER2 tema` -> POST /ping-pong-papas
- `contexto:` o referencia a archivos -> POST /ping-pong-contextos
- `PROVIDER:MODELO pregunta` -> usar ese provider/modelo
- `PROVIDER: pregunta` -> usar provider con modelo default
- Resto -> prompt de consulta con deepseek (default)

### 3. EJECUTAR SEGUN TIPO

#### Consulta Simple (nueva o con caso)
```bash
$SSH_PREFIX 'curl -s -X POST http://10.254.0.3:8900/api/v1/ping-pong \
  -H "Content-Type: application/json" \
  -H "X-API-Key: '"$API_900_KEY"'" \
  -d "{
    \"titulo\": \"Consulta [PROYECTO_ORIGEN]: [TEMA_CORTO]\",
    \"provider\": \"[PROVIDER]\",
    \"model\": \"[MODELO_O_NULL]\",
    \"proyecto_origen\": \"[PROYECTO_ORIGEN]\",
    \"caso_id\": [CASO_ID_O_NULL],
    \"prompt\": \"[LA_PREGUNTA]\"
  }"'
```

#### Brave Search (busquedas web)
```bash
$SSH_PREFIX 'curl -s -X POST http://10.254.0.3:8900/api/v1/ping-pong \
  -H "Content-Type: application/json" \
  -H "X-API-Key: '"$API_900_KEY"'" \
  -d "{
    \"titulo\": \"Brave Search [PROYECTO_ORIGEN]: [TEMA_CORTO]\",
    \"provider\": \"brave\",
    \"proyecto_origen\": \"[PROYECTO_ORIGEN]\",
    \"prompt\": \"[BUSQUEDA]\"
  }"'
```

**Brave** devuelve resultados de busqueda web, no genera texto. Util para:
- Buscar documentacion actualizada
- Verificar hechos recientes
- Encontrar repos, paquetes, precios

#### Web Search Integrado (NUEVO v2.11.0)

**Diferencia con Brave:** `provider: "brave"` solo busca. `web_search` busca + inyecta resultados en el LLM para que responda con informacion actualizada.

**Flujo:** Request -> Cache -> Knowledge Base -> Web Search -> Provider -> Response

**3 formatos del parametro `web_search`:**

1. **Simple** (busca usando el prompt como query):
```bash
$SSH_PREFIX 'curl -s -X POST http://10.254.0.3:8900/api/v1/ping-pong \
  -H "Content-Type: application/json" \
  -H "X-API-Key: '"$API_900_KEY"'" \
  -d "{
    \"titulo\": \"WebSearch [PROYECTO_ORIGEN]: [TEMA]\",
    \"provider\": \"[PROVIDER]\",
    \"proyecto_origen\": \"[PROYECTO_ORIGEN]\",
    \"prompt\": \"[PREGUNTA]\",
    \"web_search\": true
  }"'
```

2. **Con configuracion** (query custom, max_results, freshness):
```bash
$SSH_PREFIX 'curl -s -X POST http://10.254.0.3:8900/api/v1/ping-pong \
  -H "Content-Type: application/json" \
  -H "X-API-Key: '"$API_900_KEY"'" \
  -d "{
    \"titulo\": \"WebSearch [PROYECTO_ORIGEN]: [TEMA]\",
    \"provider\": \"[PROVIDER]\",
    \"proyecto_origen\": \"[PROYECTO_ORIGEN]\",
    \"prompt\": \"[PREGUNTA]\",
    \"web_search\": {\"query\": \"[BUSQUEDA]\", \"max_results\": 5, \"freshness\": \"pm\"}
  }"'
```

3. **Multi-query** (varias busquedas simultaneas):
```bash
$SSH_PREFIX 'curl -s -X POST http://10.254.0.3:8900/api/v1/ping-pong \
  -H "Content-Type: application/json" \
  -H "X-API-Key: '"$API_900_KEY"'" \
  -d "{
    \"titulo\": \"WebSearch [PROYECTO_ORIGEN]: [TEMA]\",
    \"provider\": \"[PROVIDER]\",
    \"proyecto_origen\": \"[PROYECTO_ORIGEN]\",
    \"prompt\": \"[PREGUNTA]\",
    \"web_search\": {\"query\": [\"[Q1]\", \"[Q2]\"], \"max_results\": 3}
  }"'
```

**Parametros de web_search (objeto):**

| Parametro | Default | Descripcion |
|-----------|---------|-------------|
| `enabled` | true | Activar/desactivar |
| `query` | (usa prompt) | String o array de strings |
| `max_results` | 5 | 1-10 resultados por query |
| `search_lang` | "es" | Idioma de busqueda |
| `country` | "MX" | Pais de busqueda |
| `freshness` | null | null=todo, pd=dia, pw=semana, pm=mes, py=anio |

**En debates (papas):** busca UNA VEZ al inicio, resultados se inyectan a todos los providers.

**Rate limits:** 1 req/seg, 2000/mes. Degradacion: 3 fallos consecutivos -> 5 min offline automatico.

#### Web Search en Debate
```bash
$SSH_PREFIX 'curl -s -X POST http://10.254.0.3:8900/api/v1/ping-pong-papas \
  -H "Content-Type: application/json" \
  -H "X-API-Key: '"$API_900_KEY"'" \
  -d "{
    \"titulo\": \"Debate+WS [PROYECTO_ORIGEN]: [TEMA]\",
    \"proyecto_origen\": \"[PROYECTO_ORIGEN]\",
    \"providers\": [\"[PROVIDER1]\", \"[PROVIDER2]\"],
    \"initial_prompt\": \"[TEMA_DEL_DEBATE]\",
    \"iterations\": 3,
    \"web_search\": true
  }"'
```

#### Debate con Archivos (NUEVO v2.14.0)

Enviar archivos a un debate multi-IA. Los archivos se inyectan en initial_prompt.
La API valida tokens contra el provider con menor limite + headroom para turnos.

```bash
jq -n \
  --arg titulo "Review [PROYECTO_ORIGEN]: [TEMA]" \
  --arg prompt "[INSTRUCCION]" \
  --arg origen "[PROYECTO_ORIGEN]" \
  --arg file1 "$(cat /path/to/file1.py)" \
  --arg file2 "$(cat /path/to/file2.py)" \
  '{titulo:$titulo, providers:["deepseek","gemini"],
    initial_prompt:$prompt, proyecto_origen:$origen, iterations:3,
    files:[{name:"file1.py",content:$file1,language:"python"},
           {name:"file2.py",content:$file2,language:"python"}]}' \
  | $SSH_PREFIX 'curl -s -X POST http://10.254.0.3:8900/api/v1/ping-pong-papas \
      -H "Content-Type: application/json" \
      -H "X-API-Key: '"$API_900_KEY"'" -d @-'
```

**Respuesta extra con files_info:**
- `files_count`: numero de archivos
- `files_tokens`: tokens consumidos por archivos
- `debate_headroom`: tokens reservados para turnos del debate
- `min_provider_limit`: limite del provider mas restrictivo

**Error 413:** si archivos exceden capacidad, usar gemini (1M) o reducir archivos.

#### Hilos - OpenAI Assistants (ping-pong-hilos)

Chat con threads persistentes de OpenAI Assistants. Util para conversaciones largas con memoria del lado de OpenAI.

```bash
$SSH_PREFIX 'curl -s -X POST http://10.254.0.3:8900/api/v1/ping-pong-hilos \
  -H "Content-Type: application/json" \
  -H "X-API-Key: '"$API_900_KEY"'" \
  -d "{
    \"titulo\": \"Hilo [PROYECTO_ORIGEN]: [TEMA]\",
    \"proyecto_origen\": \"[PROYECTO_ORIGEN]\",
    \"prompt\": \"[PREGUNTA]\"
  }"'
```

#### Ciclo Ping Pong con Busquedas (automejora iterativa)

**Proceso:** LLM A responde la pregunta. Si necesita info de internet, pide busquedas. LLM B las ejecuta con web_search. LLM A mejora su respuesta. Repite hasta satisfecho o max iteraciones.

**a) Confirmacion obligatoria antes de ejecutar:**

Antes de empezar el ciclo, SIEMPRE mostrar al usuario:
```
CICLO PING PONG CON BUSQUEDAS

Este modo ejecuta un ciclo iterativo de automejora:
1. LLM A ([PROVIDER_A]) responde tu pregunta
2. Si necesita info de internet, pide busquedas especificas
3. LLM B ([PROVIDER_B]) ejecuta las busquedas con web_search
4. LLM A recibe los resultados y mejora su respuesta
5. Repite hasta que LLM A este satisfecho (max [MAX] iteraciones)

Pregunta: [PREGUNTA]
Confirmar? (s/n)
```

Si el usuario no confirma, cancelar.

**b) Constantes y defaults:**
- `MAX_ITERACIONES`: 5
- LLM A (respondedor) default: `deepseek`
- LLM B (buscador) default: `gemini`
- Si el usuario especifico providers: usar los indicados

**c) Sufijo para el prompt de LLM A:**

Agregar al final del prompt del usuario el siguiente sufijo (reemplazar [N] con iteracion actual):

```
---
INSTRUCCION ADICIONAL SOBRE BUSQUEDAS WEB:
Se que no tienes acceso directo a internet, pero yo si puedo buscar informacion actualizada por ti.
Si consideras que tu respuesta se beneficiaria de informacion de internet (datos recientes, documentacion actualizada, precios, versiones, benchmarks, estadisticas, comparativas, etc.), incluye al FINAL de tu respuesta una seccion con el siguiente formato exacto:

[BUSQUEDAS_SOLICITADAS]
1. QUERY: <lo que quieres buscar textualmente> | MOTIVO: <por que necesitas esta informacion y como mejorara tu respuesta>
2. QUERY: <otra busqueda> | MOTIVO: <por que>
[/BUSQUEDAS_SOLICITADAS]

Reglas:
- Maximo 3 busquedas por iteracion (se conciso y estrategico)
- Las queries deben ser especificas y en el idioma mas efectivo para encontrar resultados
- Si tu respuesta ya es completa y precisa, NO incluyas la seccion [BUSQUEDAS_SOLICITADAS]
- Responde siempre en espanol

Nota: ya se han realizado [N] iteraciones de busqueda de un maximo de 5.
---
```

**d) Flujo paso a paso:**

**Iteracion 0 (respuesta inicial):**
```bash
$SSH_PREFIX 'curl -s -X POST http://10.254.0.3:8900/api/v1/ping-pong \
  -H "Content-Type: application/json" \
  -H "X-API-Key: '"$API_900_KEY"'" \
  -d "{
    \"titulo\": \"Ciclo [PROYECTO_ORIGEN]: [TEMA_CORTO]\",
    \"provider\": \"[PROVIDER_A]\",
    \"model\": \"[MODELO_A_O_NULL]\",
    \"proyecto_origen\": \"[PROYECTO_ORIGEN]\",
    \"caso_id\": [CASO_ID_O_NULL],
    \"prompt\": \"[PREGUNTA_ORIGINAL + SUFIJO_CON_N=0]\"
  }"'
```

Guardar `ticket_id` de la respuesta como `TICKET_ID_A`.

**Parsear respuesta de LLM A:**
- Buscar bloque `[BUSQUEDAS_SOLICITADAS]...[/BUSQUEDAS_SOLICITADAS]` en la respuesta
- Si NO hay bloque: ciclo termina, la respuesta es final
- Si hay bloque: extraer queries (max 3 por iteracion)

**Iteraciones 1-N (busqueda + mejora):**

Para cada query solicitada por LLM A, ejecutar busqueda con LLM B:
```bash
$SSH_PREFIX 'curl -s -X POST http://10.254.0.3:8900/api/v1/ping-pong \
  -H "Content-Type: application/json" \
  -H "X-API-Key: '"$API_900_KEY"'" \
  -d "{
    \"titulo\": \"CicloBusq [PROYECTO_ORIGEN]: [QUERY_CORTA]\",
    \"provider\": \"[PROVIDER_B]\",
    \"model\": \"[MODELO_B_O_NULL]\",
    \"proyecto_origen\": \"[PROYECTO_ORIGEN]\",
    \"prompt\": \"Busca y resume la siguiente informacion: [QUERY]. Motivo: [MOTIVO]. Da datos concretos, fechas, versiones, URLs si es posible.\",
    \"web_search\": true
  }"'
```

Guardar cada `ticket_id` en array `TICKET_IDS_B[]`.

Re-llamar LLM A continuando su ticket con los resultados:
```bash
$SSH_PREFIX 'curl -s -X POST http://10.254.0.3:8900/api/v1/ping-pong \
  -H "Content-Type: application/json" \
  -H "X-API-Key: '"$API_900_KEY"'" \
  -d "{
    \"ticket_id\": [TICKET_ID_A],
    \"provider\": \"[PROVIDER_A]\",
    \"model\": \"[MODELO_A_O_NULL]\",
    \"proyecto_origen\": \"[PROYECTO_ORIGEN]\",
    \"prompt\": \"Aqui estan los resultados de las busquedas que solicitaste:\n\n[RESULTADO_BUSQUEDA_1]\n[RESULTADO_BUSQUEDA_2]\n...\n\nCon esta nueva informacion, mejora y complementa tu respuesta anterior a la pregunta original: [PREGUNTA_ORIGINAL]\n\n[SUFIJO_CON_N=iteracion_actual]\"
  }"'
```

**Repetir** hasta que LLM A no incluya bloque `[BUSQUEDAS_SOLICITADAS]` o se alcance MAX_ITERACIONES.

**Si alcanza MAX_ITERACIONES:** hacer una ultima llamada a LLM A SIN el sufijo de busquedas para forzar respuesta final:
```bash
$SSH_PREFIX 'curl -s -X POST http://10.254.0.3:8900/api/v1/ping-pong \
  -H "Content-Type: application/json" \
  -H "X-API-Key: '"$API_900_KEY"'" \
  -d "{
    \"ticket_id\": [TICKET_ID_A],
    \"provider\": \"[PROVIDER_A]\",
    \"proyecto_origen\": \"[PROYECTO_ORIGEN]\",
    \"prompt\": \"Se alcanzo el maximo de iteraciones de busqueda. Por favor da tu respuesta FINAL y COMPLETA a la pregunta original, incorporando toda la informacion recopilada. NO solicites mas busquedas.\"
  }"'
```

**e) Tracking de tickets:**
- `TICKET_ID_A`: ticket principal (todos los turnos de LLM A van aqui)
- `TICKET_IDS_B[]`: array de tickets de busqueda (uno por iteracion de busqueda)
- Si el usuario incluyo `caso:N`, todos los tickets (A y B) lo incluyen

#### Continuar Ticket Existente
```bash
$SSH_PREFIX 'curl -s -X POST http://10.254.0.3:8900/api/v1/ping-pong \
  -H "Content-Type: application/json" \
  -H "X-API-Key: '"$API_900_KEY"'" \
  -d "{
    \"ticket_id\": [TICKET_ID],
    \"provider\": \"[PROVIDER]\",
    \"model\": \"[MODELO_O_NULL]\",
    \"proyecto_origen\": \"[PROYECTO_ORIGEN]\",
    \"prompt\": \"[PREGUNTA_SEGUIMIENTO]\"
  }"'
```

#### Debate entre 2+ IAs (ping-pong-papas)
```bash
$SSH_PREFIX 'curl -s -X POST http://10.254.0.3:8900/api/v1/ping-pong-papas \
  -H "Content-Type: application/json" \
  -H "X-API-Key: '"$API_900_KEY"'" \
  -d "{
    \"titulo\": \"Debate [PROYECTO_ORIGEN]: [TEMA]\",
    \"proyecto_origen\": \"[PROYECTO_ORIGEN]\",
    \"caso_id\": [CASO_ID_O_NULL],
    \"providers\": [\"[PROVIDER1]\", \"[PROVIDER2]\"],
    \"models\": [\"[MODELO1]\", \"[MODELO2]\"],
    \"initial_prompt\": \"[TEMA_DEL_DEBATE]\",
    \"iterations\": 3
  }"'
```

**CRITICO:** El campo se llama `initial_prompt`, NO `prompt`. Error comun.

**Consensus threshold automatico:**
- 2 IAs = 0.80
- 3 IAs = 0.70
- 4 IAs = 0.60
- 5 IAs = 0.50

**Terminacion del debate:**
- **consenso_alcanzado**: similitud >= threshold, termina anticipado
- **max_iteraciones**: sin consenso, genera sintesis final automatica
- **estancamiento**: moderador detecta sin argumentos nuevos

#### Consulta con Archivos (ping-pong-contextos)

Enviar archivos de codigo, docs o planes a una IA para revision/analisis.

**Elegir provider segun tamano total de archivos:**
- **< 64K tokens**: deepseek (barato, bueno)
- **64K-128K tokens**: openai/gpt-4o
- **> 128K tokens**: gemini (1M context window)

**Patron con jq (recomendado para archivos grandes):**
```bash
jq -n \
  --arg titulo "Review [PROYECTO_ORIGEN]: [TEMA]" \
  --arg provider "[PROVIDER]" \
  --arg prompt "[INSTRUCCION]" \
  --arg origen "[PROYECTO_ORIGEN]" \
  --arg file1 "$(cat /path/to/file1.ts)" \
  --arg file2 "$(cat /path/to/file2.ts)" \
  '{titulo:$titulo, provider:$provider, prompt:$prompt,
    proyecto_origen:$origen,
    files:[{name:"file1.ts",content:$file1},{name:"file2.ts",content:$file2}]}' \
  | $SSH_PREFIX 'curl -s -X POST http://10.254.0.3:8900/api/v1/ping-pong-contextos \
      -H "Content-Type: application/json" \
      -H "X-API-Key: '"$API_900_KEY"'" -d @-'
```

**Patron inline (archivos pequenos):**
```bash
$SSH_PREFIX 'curl -s -X POST http://10.254.0.3:8900/api/v1/ping-pong-contextos \
  -H "Content-Type: application/json" \
  -H "X-API-Key: '"$API_900_KEY"'" \
  -d "{
    \"titulo\": \"Review [PROYECTO_ORIGEN]: [TEMA]\",
    \"provider\": \"[PROVIDER]\",
    \"prompt\": \"[INSTRUCCION]\",
    \"proyecto_origen\": \"[PROYECTO_ORIGEN]\",
    \"files\": [{\"name\": \"[FILENAME]\", \"content\": \"[CONTENIDO_ESCAPADO]\"}]
  }"'
```

**Campos adicionales de contextos:**
- `files`: array de `{name, content}` - REQUERIDO
- `ticket_id`: continuar conversacion (contexto persiste entre turnos)
- `caso_id`: agrupar en un caso
- La respuesta incluye `context_info` con `usage_percent`, `chars`, `tokens`, `files_breakdown`

**Errores comunes:**
- **No usar jq**: Escapar contenido manualmente rompe JSON. Siempre usar `jq -n --arg`
- **Error 413 Payload Too Large**: Cambiar a gemini o reducir archivos
- **cat en --arg**: El `$(cat file)` se ejecuta localmente, no en el server remoto. Archivos deben ser accesibles localmente

#### Ver Caso
```bash
$SSH_PREFIX 'curl -s -H "X-API-Key: '"$API_900_KEY"'" http://10.254.0.3:8900/api/v1/casos/[CASO_ID]'
```

#### Ver Tickets de un Caso
```bash
$SSH_PREFIX 'curl -s -H "X-API-Key: '"$API_900_KEY"'" http://10.254.0.3:8900/api/v1/casos/[CASO_ID]/tickets'
```

#### Ver Ticket Completo
```bash
$SSH_PREFIX 'curl -s -H "X-API-Key: '"$API_900_KEY"'" http://10.254.0.3:8900/api/v1/tickets/[TICKET_ID]'
```

#### Crear Caso
```bash
$SSH_PREFIX 'curl -s -X POST http://10.254.0.3:8900/api/v1/casos \
  -H "Content-Type: application/json" \
  -H "X-API-Key: '"$API_900_KEY"'" \
  -d "{
    \"titulo\": \"[TITULO]\",
    \"descripcion\": \"[DESC_OPCIONAL]\",
    \"prioridad\": \"media\",
    \"tags\": [\"[PROYECTO_ORIGEN]\", \"[TAG1]\", \"[TAG2]\"]
  }"'
```

#### Listar Casos Abiertos
```bash
$SSH_PREFIX 'curl -s -H "X-API-Key: '"$API_900_KEY"'" "http://10.254.0.3:8900/api/v1/casos?estado=abierto"'
```

#### Listar Providers
```bash
$SSH_PREFIX 'curl -s -H "X-API-Key: '"$API_900_KEY"'" http://10.254.0.3:8900/api/v1/ping-pong/providers'
```

#### Ver Help de API (GET)
```bash
$SSH_PREFIX 'curl -s -H "X-API-Key: '"$API_900_KEY"'" http://10.254.0.3:8900/api/v1/help'
```

#### Preguntar a la IA sobre la API (POST /help)
```bash
$SSH_PREFIX 'curl -s -X POST http://10.254.0.3:8900/api/v1/help \
  -H "Content-Type: application/json" \
  -H "X-API-Key: '"$API_900_KEY"'" \
  -d "{\"prompt\": \"como uso web_search?\"}"'
```

#### Listar Tickets (con filtros)
```bash
$SSH_PREFIX 'curl -s -H "X-API-Key: '"$API_900_KEY"'" "http://10.254.0.3:8900/api/v1/tickets?proyecto_origen=[PROYECTO]&estado=abierto"'
```

#### Actualizar Estado de Ticket
```bash
$SSH_PREFIX 'curl -s -X PUT http://10.254.0.3:8900/api/v1/tickets/[TICKET_ID]/estado \
  -H "Content-Type: application/json" \
  -H "X-API-Key: '"$API_900_KEY"'" \
  -d "{\"estado\": \"cerrado\"}"'
```

#### Actualizar Caso
```bash
$SSH_PREFIX 'curl -s -X PUT http://10.254.0.3:8900/api/v1/casos/[CASO_ID] \
  -H "Content-Type: application/json" \
  -H "X-API-Key: '"$API_900_KEY"'" \
  -d "{\"titulo\": \"[NUEVO_TITULO]\", \"prioridad\": \"alta\"}"'
```

#### Cerrar Caso (soft delete)
```bash
$SSH_PREFIX 'curl -s -X DELETE http://10.254.0.3:8900/api/v1/casos/[CASO_ID] \
  -H "X-API-Key: '"$API_900_KEY"'"'
```

#### Asignar Ticket a Caso
```bash
$SSH_PREFIX 'curl -s -X POST http://10.254.0.3:8900/api/v1/casos/[CASO_ID]/tickets/[TICKET_ID] \
  -H "X-API-Key: '"$API_900_KEY"'"'
```

#### Desasignar Ticket de Caso
```bash
$SSH_PREFIX 'curl -s -X DELETE http://10.254.0.3:8900/api/v1/casos/[CASO_ID]/tickets/[TICKET_ID] \
  -H "X-API-Key: '"$API_900_KEY"'"'
```

#### Eliminar Ticket
```bash
$SSH_PREFIX 'curl -s -X DELETE http://10.254.0.3:8900/api/v1/tickets/[TICKET_ID] \
  -H "X-API-Key: '"$API_900_KEY"'"'
```

#### Estadisticas del Sistema
```bash
$SSH_PREFIX 'curl -s -H "X-API-Key: '"$API_900_KEY"'" http://10.254.0.3:8900/api/v1/stats'
```

#### Auto-registrar API Key (requiere master secret + intervencion humana)
```bash
$SSH_PREFIX 'curl -s -X POST http://10.254.0.3:8900/api/v1/keys/register \
  -H "Content-Type: application/json" \
  -d "{
    \"project_code\": \"[PROYECTO_ORIGEN]\",
    \"project_name\": \"[NOMBRE_PROYECTO]\",
    \"secret\": \"<master_secret>\"
  }"'
```
**NOTA:** Requiere el master secret que solo tiene el admin. La key se muestra UNA VEZ en la respuesta.
Pedir al usuario que contacte al admin para obtener el secret.

#### Rotar API Key
```bash
$SSH_PREFIX 'curl -s -X POST http://10.254.0.3:8900/api/v1/keys/rotate \
  -H "Content-Type: application/json" \
  -d "{
    \"project_code\": \"[PROYECTO_ORIGEN]\",
    \"old_api_key\": \"[KEY_ACTUAL]\",
    \"secret\": \"<master_secret>\"
  }"'
```
**NOTA:** La key anterior sigue activa 7 dias (periodo de gracia).

#### Ver Info de Keys del Proyecto
```bash
$SSH_PREFIX 'curl -s -H "X-API-Key: '"$API_900_KEY"'" http://10.254.0.3:8900/api/v1/keys/info'
```

### 4. PROCESAR RESPUESTA

**Respuesta de consulta:**
```json
{
  "ticket_id": 123,
  "caso_id": 2,
  "turno": 1,
  "respuesta": "...",
  "provider": "deepseek",
  "model": "deepseek-reasoner",
  "tokens_usados": 1500,
  "latencia_ms": 1234
}
```

**Respuesta de debate:**
```json
{
  "ticket_id": 186,
  "caso_id": 2,
  "modo": "ping_pong_papas",
  "turnos": [
    {"turno": 1, "provider": "gemini", "model": "...", "contenido": "...", "tokens_usados": 1500, "latencia_ms": 30000},
    {"turno": 2, "provider": "deepseek", "model": "...", "contenido": "...", "tokens_usados": 1200, "latencia_ms": 25000}
  ]
}
```

**Respuesta de contextos:**
```json
{
  "ticket_id": 200,
  "respuesta": "...",
  "provider": "gemini",
  "context_info": {
    "chars": 15000,
    "tokens": 4500,
    "usage_percent": 0.45,
    "files_breakdown": [{"name": "file1.ts", "chars": 8000}, {"name": "file2.ts", "chars": 7000}]
  }
}
```

**Respuesta con web_search_info (cuando se uso web_search):**
```json
{
  "ticket_id": 500,
  "respuesta": "...",
  "provider": "gemini",
  "web_search_info": {
    "query": "FastAPI mejores practicas 2026",
    "results_count": 5,
    "searches_count": 1,
    "search_time_ms": 450,
    "sources": [
      {"title": "FastAPI Docs", "url": "https://...", "description": "...", "age": "2d"}
    ]
  }
}
```

**Respuesta de ciclo ping pong con busquedas:**
La respuesta se construye internamente a lo largo de las iteraciones. Estructura de tracking:
- `TICKET_ID_A`: ticket principal con todos los turnos de LLM A
- `TICKET_IDS_B[]`: array de tickets de busqueda (uno por cada iteracion con busquedas)
- `iteraciones`: numero de iteraciones completadas (0 = solo respuesta inicial)
- `busquedas_totales`: suma de todas las queries ejecutadas en todas las iteraciones

**Deteccion de Knowledge Base interceptando:** Si la respuesta tiene `from_knowledge_base: true` y `provider: "knowledge_base"`, la KB respondio en vez del provider. Reintentar con `"use_knowledge_base": false` en el payload.

### 5. MANEJO DE ERRORES

| Error | Causa | Solucion |
|-------|-------|----------|
| **413 Payload Too Large** | Archivos muy grandes para el provider (contextos y debates con files) | Cambiar a `gemini` (1M context) o reducir archivos |
| **503 Service Unavailable** | Provider caido/degradado | Sugerir provider alternativo (deepseek↔openai) |
| **401 API key required** | Falta header X-API-Key | Configurar `API_900_KEY` en `.env` del proyecto |
| **401 Invalid or revoked** | Key incorrecta o revocada | Pedir nueva key al admin de API 900 |
| **Connection refused** | API 900 no esta corriendo | Verificar: `$SSH_PREFIX 'curl -s http://10.254.0.3:8900/health'` |
| **SSH timeout** | Problema de red/VPN | Verificar conectividad SSH al server |
| **KB intercepta** | Knowledge Base respondio en vez del provider | Reintentar con `"use_knowledge_base": false` |
| **Timeout en debate** | Debate largo con muchas iteraciones | Reducir `iterations` o usar providers mas rapidos (groq) |
| **Ciclo excede iteraciones** | LLM A pidio busquedas en todas las iteraciones | Se forzo respuesta final sin sufijo de busquedas en la ultima llamada |

### 6. MOSTRAR RESULTADO

**Para consultas:**
```
CONSULTA A API 900

Proyecto: [PROYECTO_ORIGEN]
Pregunta: [PREGUNTA]
Provider: [PROVIDER] ([MODELO])
Ticket: #[TICKET_ID] | Caso: #[CASO_ID] | Turno: [N]

RESPUESTA:
---
[CONTENIDO DE LA RESPUESTA]
---

Tokens: [TOTAL] | Tiempo: [LATENCY]ms
```

**Para brave search:**
```
BRAVE SEARCH VIA API 900

Proyecto: [PROYECTO_ORIGEN]
Busqueda: [QUERY]
Ticket: #[TICKET_ID]

RESULTADOS:
---
[RESULTADOS DE BUSQUEDA]
---
```

**Para consultas con web search:**
```
CONSULTA + WEB SEARCH API 900

Proyecto: [PROYECTO_ORIGEN]
Pregunta: [PREGUNTA]
Provider: [PROVIDER] ([MODELO])
Ticket: #[TICKET_ID] | Caso: #[CASO_ID] | Turno: [N]
Web Search: [RESULTS_COUNT] resultados ([SEARCH_TIME]ms)

RESPUESTA:
---
[CONTENIDO DE LA RESPUESTA]
---

Fuentes web:
- [TITLE1] - [URL1] ([AGE1])
- [TITLE2] - [URL2] ([AGE2])

Tokens: [TOTAL] | Tiempo: [LATENCY]ms
```

**Para debates:**
```
DEBATE API 900

Proyecto: [PROYECTO_ORIGEN]
Tema: [TEMA]
Ticket: #[TICKET_ID] | Caso: #[CASO_ID]
Participantes: [PROVIDER1] vs [PROVIDER2]

--- TURNO 1 ([PROVIDER1] - [MODELO1]) ---
[RESPUESTA1]

--- TURNO 2 ([PROVIDER2] - [MODELO2]) ---
[RESPUESTA2]

...

Tokens totales: [TOTAL] | Tiempo: [LATENCY]ms
```

**Para contextos:**
```
REVIEW API 900

Proyecto: [PROYECTO_ORIGEN]
Archivos: [FILE1], [FILE2]
Provider: [PROVIDER] ([MODELO])
Ticket: #[TICKET_ID]
Contexto usado: [USAGE_PERCENT]%

RESPUESTA:
---
[CONTENIDO DE LA RESPUESTA]
---

Tokens: [TOTAL] | Tiempo: [LATENCY]ms
```

**Para ciclo ping pong con busquedas:**
```
CICLO PING PONG CON BUSQUEDAS - API 900

Proyecto: [PROYECTO_ORIGEN]
Pregunta original: [PREGUNTA]
LLM A (respondedor): [PROVIDER_A] ([MODELO_A])
LLM B (buscador): [PROVIDER_B] ([MODELO_B])
Ticket principal: #[TICKET_ID_A]
Iteraciones: [N] de [MAX]

--- ITERACION 0 (respuesta inicial) ---
[RESPUESTA_INICIAL]
Busquedas solicitadas: [QUERIES]

--- ITERACION 1 (busqueda + mejora) ---
Ticket busqueda: #[TICKET_ID_B_1]
Queries: [QUERIES_EJECUTADAS]
[RESPUESTA_MEJORADA]

--- ITERACION N ... ---

--- RESPUESTA FINAL ---
[RESPUESTA_FINAL_LIMPIA (sin bloque BUSQUEDAS_SOLICITADAS)]

Resumen: [N] iteraciones, [M] busquedas totales, tickets #A #B1 #B2...
```

**Para casos:**
```
CASO #[ID]: [TITULO]

Estado: [ESTADO] | Prioridad: [PRIORIDAD]
Tickets: [COUNT]
Proyectos: [LISTA]
Tags: [TAGS]

Tickets en este caso:
- #[TID1]: [TITULO1] ([MODO])
- #[TID2]: [TITULO2] ([MODO])
```

### 7. SUGERIR SIGUIENTE ACCION

Al final de cada consulta/debate, sugiere:
- Si fue consulta nueva sin caso: "Quieres vincular este ticket a un caso?"
- Si fue con caso: "Ticket #X vinculado a caso #Y. Continuar con `ticket:X [pregunta]`"
- Si fue debate: "Debate guardado en ticket #X. Continuar con `ticket:X [pregunta]` para seguir la discusion"
- Si fue contextos: "Review guardado en ticket #X. Continuar con `ticket:X [pregunta]` (contexto persiste)"
- Si fue brave search: "Resultados guardados en ticket #X. Profundizar con `ticket:X [pregunta]`"
- Si fue ciclo de busquedas: "Ciclo completado en [N] iteraciones con [M] busquedas. Ticket principal #X. Continuar con `ticket:X [pregunta]`"

### 8. AUTO-SAVE (Opcional)

Si el usuario quiere guardar la respuesta localmente:
```bash
mkdir -p docs/consultas-900
# Guardar respuesta como markdown
echo "[RESPUESTA_FORMATEADA]" > docs/consultas-900/consulta-[TICKET_ID].md
```

## Parametros Completos

### ping-pong (consulta simple)

| Parametro | Requerido | Descripcion |
|-----------|-----------|-------------|
| `titulo` | SI (nuevo) | Titulo corto para tracking |
| `provider` | SI | Ver lista de providers |
| `prompt` | SI | La pregunta o tema |
| `proyecto_origen` | SI | Detectado desde PROJECT.yaml |
| `model` | NO | Modelo especifico (usa default si no se indica) |
| `caso_id` | NO | Vincular a caso existente |
| `ticket_id` | NO | Continuar ticket existente |
| `use_knowledge_base` | NO | boolean, default true. **Poner false para consultas creativas/opinion/UX** |
| `temperature` | NO | float |
| `max_tokens` | NO | int (max 16000) |
| `web_search` | NO | true, o objeto {query, max_results, freshness, search_lang, country} |
| `context` | NO | Contexto adicional como string |
| `metadata` | NO | Objeto libre |

### ping-pong-papas (debate)

| Parametro | Requerido | Descripcion |
|-----------|-----------|-------------|
| `titulo` | SI | Titulo del debate |
| `providers` | SI | Array de 2+ providers: `["gemini", "deepseek"]` |
| `initial_prompt` | SI | Tema del debate (**NO "prompt"**) |
| `proyecto_origen` | SI | Detectado desde PROJECT.yaml |
| `models` | NO | Array de modelos (mismo orden que providers) |
| `iterations` | NO | Rondas de debate (default auto) |
| `consensus_threshold` | NO | 0.0-1.0 (auto-calculado si omitido) |
| `caso_id` | NO | Vincular a caso existente |
| `web_search` | NO | true, o objeto (busca UNA VEZ al inicio del debate) |
| `files` | NO | Array de {name, content, language} - archivos para el debate (v2.14.0) |

### ping-pong-contextos (archivos)

| Parametro | Requerido | Descripcion |
|-----------|-----------|-------------|
| `titulo` | SI | Titulo del review |
| `provider` | SI | Ver tabla de context windows para elegir |
| `prompt` | SI | Instruccion sobre que hacer con los archivos |
| `files` | SI | Array de `{name, content}` |
| `proyecto_origen` | SI | Detectado desde PROJECT.yaml |
| `model` | NO | Modelo especifico |
| `caso_id` | NO | Vincular a caso |
| `ticket_id` | NO | Continuar (contexto persiste) |
| `web_search` | NO | true, o objeto (busca antes de enviar al provider) |

## Ejemplos de Uso

```
/consultar-900 cual es el mejor approach para Redis?
/consultar-900 caso:2 como implemento el worker de colas?
/consultar-900 ticket:185 dame codigo de ejemplo para el health check
/consultar-900 gemini:gemini-3.1-pro-preview explicame WebSockets
/consultar-900 deepseek:deepseek-reasoner analiza este approach
/consultar-900 debate gemini vs deepseek Redis vs RabbitMQ para colas
/consultar-900 caso:2 debate deepseek:deepseek-reasoner vs grok:grok-3 Cloudflare vs nginx
/consultar-900 contexto: revisa src/index.ts y src/routes/main.ts, busca vulnerabilidades
/consultar-900 brave: mejores practicas fastapi 2026
/consultar-900 websearch: mejores frameworks Python 2026
/consultar-900 ws:3m gemini: comparativa Bun vs Deno 2026
/consultar-900 hilos: necesito ayuda con mi proyecto de machine learning
/consultar-900 qwen: explicame MoE (Mixture of Experts)
/consultar-900 kimi: analiza este patron de diseno
/consultar-900 help como uso web_search?
/consultar-900 ver caso:2
/consultar-900 listar casos
/consultar-900 crear caso: Implementacion Alta Disponibilidad
/consultar-900 providers
/consultar-900 ciclo: cuales son las mejores practicas de seguridad para APIs en 2026?
/consultar-900 ciclo gemini deepseek: comparativa de frameworks backend Python 2026
/consultar-900 ciclo openai:gpt-5.3 gemini: estado actual de WebAssembly en produccion
/consultar-900 ciclo de busquedas: que tan maduro esta Bun.js para produccion?
/consultar-900 ciclo automejora: mejores bases de datos vectoriales 2026
/consultar-900 help
```

## Notas

- API 900 esta en server003:8900 (v2.15.0)
- **Auth**: API 900 requiere API key en todas las llamadas (excepto /health y /docs)
- **Key**: Cada proyecto tiene su key. Configurar en `.env` como `API_900_KEY=900-xxx-xxx`
- **Obtener key**: POST /keys/register (requiere master secret del admin, intervencion humana)
- **Rotar key**: POST /keys/rotate (key anterior activa 7 dias de gracia)
- **Sin key**: HTTP 401 - pedir al usuario que contacte admin de API 900
- `proyecto_origen` se detecta desde PROJECT.yaml automaticamente
- Los tickets se guardan automaticamente en la API
- Un caso puede agrupar tickets de consultas, debates, contextos e hilos
- Usa `ticket:N` para continuar conversaciones (ahorra contexto)
- Para debates, especifica ambos modelos: `debate PROV1:MOD1 vs PROV2:MOD2 tema`
- DeepSeek es el provider default por costo/calidad
- **Brave**: para busquedas web puras, no genera texto -- devuelve resultados de busqueda
- **Web Search**: busca + inyecta en LLM. Usar `web_search: true` o `websearch:` en el input
- **Web Search vs Brave**: brave solo busca. web_search busca y luego el provider responde usando los resultados
- **Knowledge Base**: por default intercepta si encuentra match semantico. Usar `use_knowledge_base: false` para consultas creativas/opinion/UX
- **Providers v2.11.0**: openai, deepseek, gemini, grok, groq, **qwen** (nuevo), **kimi** (nuevo), brave
- **MCP expandido** (v2.15.0): disponible en `http://10.254.0.3:8900/mcp?api_key=TU_KEY` (key via query param)
  - **Transporte**: Streamable HTTP (SSE)
  - **Tools**: consulta_ia, debate_ias, buscar_web, investigar, listar_tickets, ver_ticket, actualizar_ticket, crear_caso, ayuda_api, listar_providers, obtener_estadisticas
  - **Resources**: ticket://{id}, caso://{id}, stats://general, providers://
  - **Registro en Claude Code**: `claude mcp add 900-api http http://10.254.0.3:8900/mcp`
  - **Ejemplo Python**:
    ```python
    from fastmcp import Client
    async with Client("http://10.254.0.3:8900/mcp") as client:
        result = await client.call_tool("consulta_ia", {
            "titulo": "Mi consulta",
            "provider": "deepseek",
            "prompt": "Tu pregunta",
            "proyecto_origen": "045"
        })
    ```
