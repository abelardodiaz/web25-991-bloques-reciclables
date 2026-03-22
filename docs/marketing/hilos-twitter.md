# Hilos de Twitter - ulfblk

## Hilo 1: Introduccion al ecosistema

1/ Cada vez que arranco un proyecto con FastAPI paso 2 semanas configurando lo mismo: JWT, RBAC, SQLAlchemy async, multitenancy, health checks. Harto de eso, hice algo al respecto.

2/ Cree ulfblk: paquetes pip composables para FastAPI. No es un framework monolitico como Django o Laravel. No es un boilerplate que copias y rezas. Son paquetes independientes que instalas y combinas:

uv add ulfblk-core ulfblk-db ulfblk-auth

3/ 20 lineas y tienes API con todo:

from ulfblk_core import create_app
app = create_app(service_name="mi-api")

Health check, request IDs, timing, exception handlers, logging. Ya incluido.

4/ Los modelos son TUYOS. ulfblk te da mixins, tu compones:

class User(Base, TimestampMixin, SoftDeleteMixin):
    email = Column(String, unique=True)
    tenant_id = Column(String)

Nada de modelos User impuestos como Django. Tu defines tus campos, relaciones, y logica.

5/ Multitenancy con PostgreSQL RLS transparente via contextvars. Supabase lo tiene pero te ata a su plataforma. ulfblk te da RLS en tu propio PostgreSQL, sin vendor lock-in.

6/ Testing sin dolor. uv add --dev ulfblk-testing y pytest ya tiene fixtures: JWT tokens falsos, HTTP client autenticado, DB in-memory. Cero config.

7/ Stripe + multitenancy? uv add ulfblk-billing ulfblk-multitenant. Las suscripciones se aislan automaticamente por tenant sin codigo extra. Asi con todo: Redis, webhooks, rate limiting. Compones lo que necesitas.

8/ Para el dev que prefiere herramientas sobre frameworks. Open source, MIT, 100+ tests.

github.com/abelardodiaz/web25-991-bloques-reciclables

---

## Hilo 2: Posicionamiento vs competencia

1/ FastAPI es increible pero su ecosistema esta fragmentado. Quieres auth? fastapi-users. ORM? sqlmodel. Multitenancy? No existe. Billing? Hazlo tu. Testing? Arreglalo tu. Cada paquete es de un autor diferente, con APIs diferentes.

2/ Piccolo intento resolverlo pero te ata a su ORM propietario. Si ya sabes SQLAlchemy, tienes que aprender otro ORM. No gracias.

3/ Por eso cree ulfblk: 17 paquetes pip que cubren auth, DB, multitenancy, billing, testing, Redis, gateway - todos disenados para funcionar juntos Y por separado. Todos usan SQLAlchemy estandar.

4/ La killer feature: multitenancy con PostgreSQL RLS. django-tenants lo tiene para Django. Supabase lo tiene en su plataforma. Para FastAPI? No existia. ulfblk-multitenant lo resuelve con contextvars, transparente, sin vendor lock-in.

5/ Y no es solo backend. 6 paquetes npm para frontend: api-client con interceptors, auth-react con hooks, admin panel con react-admin. Full stack composable.

6/ Lo que NO somos: no somos Django (no te damos todo junto). No somos un boilerplate (no copias codigo). Somos herramientas que instalas, actualizas, y compones. Como npm packages pero para Python SaaS.

7/ Open source, MIT. 100+ tests, publicado en PyPI y npm. Si construyes SaaS con FastAPI, echale un ojo.

github.com/abelardodiaz/web25-991-bloques-reciclables

---

## Hilo 3: EduSync - la prueba de fuego

1/ "Con estos bloques puedes construir un SaaS real?" Me lo preguntaron. Asi que lo hice. Construi una plataforma educativa completa con 11 de los 14 bloques Python de ulfblk. 31 tests. Backend + frontend. Desde cero.

2/ EduSync tiene: cursos con lecciones, inscripciones con tracking de progreso, sesiones en vivo con instructores, tutor IA con RAG, reglas de automation para certificaciones, billing Stripe, cache Redis, y multitenancy. No es un TODO app.

3/ Lo dividi en 4 fases, cada una agregando bloques sobre la anterior:

Fase 1: core + db + scheduling + calendar (lo basico)
Fase 2: auth + multitenant (JWT RBAC, tenant isolation)
Fase 3: ai-rag + automation + notifications (inteligencia)
Fase 4: billing + redis (negocio + performance)

4/ El scheduling de sesiones en vivo reutiliza AppointmentMixin y generate_slots() directamente de ulfblk-scheduling. El mismo codigo que maneja citas medicas maneja clases virtuales. Cero lineas de scheduling nuevo.

5/ Lo mas interesante: la automation. Tres reglas en 30 lineas:
- Completas todas las lecciones? enrollment.status = "completed"
- Score >= 80 en final exam? Notificacion de certificado
- Regla deshabilitada? No se ejecuta

RuleEngine de ulfblk-automation, sin if/elif chains.

6/ Auth con 3 roles reales (student, instructor, admin). El estudiante ve cursos. El instructor crea cursos. El admin ve usuarios. Cada uno tiene su dashboard. No es auth de juguete - es RBAC con JWT RS256.

7/ El test mas revelador: tenant isolation. Login como Acme, ves cursos de Acme. Login como Globex, ves cursos de Globex. Misma base de datos, aislamiento transparente via TenantContext. En produccion seria PostgreSQL RLS.

8/ 31 tests, 84 en total del repo, 0 failures. El codigo esta en examples/edusync/ con backend Python + frontend Next.js. Juzga tu mismo.

github.com/abelardodiaz/web25-991-bloques-reciclables

---

## Hilo 4: El ROI real de reciclar modulos

1/ "Construir bloques reutilizables es perder el tiempo." Lo escucho seguido. Asi que medi cuanto ahorre construyendo EduSync (plataforma educativa SaaS) con ulfblk vs desde cero. Los numeros:

2/ Auth JWT con RBAC y RS256: 2 dias desde cero. Con ulfblk-auth: 1 hora (import JWTManager, generar keys, 5 lineas de config). Ahorro: 90%.

3/ Scheduling completo (slots, conflictos, availability): 3 dias desde cero. Con ulfblk-scheduling: 0 horas. Ya existia de la receta anterior (bot-citas). Reutilice AppointmentMixin y generate_slots() sin cambiar una linea. Ahorro: 100%.

4/ Rule engine para automation: 2 dias desde cero (disenar modelo de reglas, evaluador de condiciones, handlers). Con ulfblk-automation: 30 minutos para definir 3 reglas. Ahorro: 95%.

5/ Multitenancy con aislamiento de datos: 3 dias desde cero (contextvars, middleware, filtros en queries). Con ulfblk-multitenant: 1 hora (set_current_tenant() y filtro manual en SQLite, RLS automatico en PostgreSQL). Ahorro: 90%.

6/ Total estimado: 13 dias de trabajo senior comprimidos en 4 horas. No porque el codigo sea trivial, sino porque las decisiones ya estan tomadas. Como manejar timezone con SQLite. Como detectar conflictos de horario. Como aislar tenants. Esas decisiones cuestan mas que el codigo.

7/ El truco no es que los bloques sean brillantes. Es que cada uno tiene tests (450+ en total), cada uno resuelve UN problema, y ninguno depende de los demas. Usas 4 para un bot de citas. Usas 11 para una plataforma educativa. Usas 14 si quieres todo.

8/ El valor real de un ecosistema composable no es ahorrarte lineas de codigo. Es ahorrarte las 2am debugging un edge case de timezone que alguien ya resolvio, testeo, y documento. Eso es lo que reciclas.

github.com/abelardodiaz/web25-991-bloques-reciclables
