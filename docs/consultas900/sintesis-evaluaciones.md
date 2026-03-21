# Sintesis de Evaluaciones Externas

> Fuentes: Gemini (ticket 760) + DeepSeek (ticket 766) + Claude 991 - 2026-03-20
> Cada fila es un tema accionable. Trabajar en planes independientes por fila.

---

| # | Tema | Consenso | Destacado Gemini | Destacado DeepSeek | Nota Claude 991 | Prioridad |
|---|------|----------|------------------|--------------------| ----------------|----------|
| 1 | **bloque-core insuficiente** | Demasiado basico para ser fundacion de ecosistema | Hardcoding en health_router es "inaceptable" (`version="0.1.0"`, `service="api"` estaticos) | Falta CORS, rate limiting, security headers | CORS no va en core (es config por proyecto, ver #8). Rate limiting ya existe en bloque-gateway. Core debe ser minimo. Falta: re-exports en `__init__.py`, `create_app()` factory, threshold configurable en TimingMiddleware | CRITICA |
| 2 | **Exception handling** | Falta Global Exception Handler que use ErrorResponse | Middleware que capture HTTPException + ValueError + errores BD | Exception handlers globales HTTP -> JSON | De acuerdo con ambas. ErrorResponse ya existe en schemas pero nada lo usa automaticamente | CRITICA |
| 3 | **Historia de base de datos** | Falta DB/migraciones/Alembic | Mixins SQLAlchemy (AuthMixin, BillingMixin) en vez de modelos concretos | Falta database session/engine factory en core | Session factory NO en core (forzaria SQLAlchemy como dep obligatoria). Mejor en bloque-db separado. Mixins de Gemini es la idea correcta | CRITICA |
| 4 | **Composabilidad no demostrada** | Independencia de bloques no probada en practica | "La promesa es una ilusion" - relaciones SQLAlchemy requieren conocer otros modelos | Version hell: sin compatibility matrix entre bloques | Gemini confunde arquitectura con limitacion. Bloques exportan mixins e infraestructura, NO modelos concretos. Relaciones SQLAlchemy las define el dev en SU app. Probado con 18 integration tests (model composition + auth+DB + multitenant+DB + full stack FastAPI). COMPATIBILITY.md documenta matrix | ALTA |
| 5 | **bloque-testing** | Falta paquete de testing con fixtures | Clientes HTTP falsos, generadores JWT de prueba, config DB en memoria para RLS | Testing framework integrado para apps multi-bloque | De acuerdo con ambas. NO depender de todos los bloques - usar optional deps ([auth], [db]). Registrar como pytest plugin via entry_points. Extraer fixtures de bloque-auth/tests (RSA keys, JWTManager) y bloque-db/tests (engine, session). create_jwt_manager importa JWTManager en runtime para no forzar bloque-auth como dep | ALTA |
| 6 | **Versionado automatizado** | Falta automatizacion de versiones en monorepo | Changesets adaptado para `uv publish` - sin esto "el monorepo colapsara" | (no profundiza en tooling) | -- | ALTA |
| 7 | **Distribucion PyPI/npm** | No publicado = no usable externamente | `uv add bloque-core` fallara sin PyPI | "Es codigo interno reempaquetado" sin publicacion | -- | ALTA |
| 8 | **Config centralizada** | Falta gestion unificada de configuracion | Registro central - bloques no deben leer env vars independientemente | BaseSettings con validacion (dotenv, secrets) | BloqueSettings YA es la solucion. Migrados 4 bloques (redis, gateway, channels, billing) de @dataclass a BloqueSettings con env_prefix por clase (BLOQUE_REDIS_, BLOQUE_BILLING_, etc). Env vars automaticas, .env, validacion. Ejemplo arreglado para no usar os.environ.get() | MEDIA |
| 9 | **Competencia y diferenciacion** | No comunica ventaja clara vs alternativas | vs SaaS Pegasus/ShipFast: dependencias vs codigo fuente = mas rigido | vs Django/Supabase, tabla comparativa. Falta "killer feature" | -- | MEDIA |
| 10 | **Ejemplo integracion real** | Pausar bloques nuevos, enfocarse en demo E2E | "Integration sprint" con IoC y Mixins | CLI unica `bloque create`, tutorial "Build SaaS in 1 hour". Puntuacion: 5/10 | Reescrito examples/saas-multitenant/ de dicts en memoria a SQLAlchemy real. 4 bloques (core+auth+db+multitenant). SQLite zero-config default, PostgreSQL via env var. Modelos con mixins composables, FK relationships, soft delete. No frontend en este sprint (es otro ambito) | ALTA |

---

## Como usar esta tabla

Cada fila es un plan independiente. Para trabajar un tema:
1. Crear plan referenciando el # de fila
2. Leer las evaluaciones completas para contexto detallado:
   - `eval-proyecto-gemini-ticket-760.md`
   - `eval-proyecto-deepseek-ticket-766.md`
3. Implementar y marcar como resuelto

## Orden sugerido de ejecucion

**Sprint 1 (fundacion):** #1, #2, #3 - Arreglar bloque-core
**Sprint 2 (validacion):** #4, #5, #10 - Demostrar composabilidad con ejemplo real
**Sprint 3 (distribucion):** #6, #7 - Publicar en PyPI/npm
**Sprint 4 (posicionamiento):** #8, #9 - Config y diferenciacion
