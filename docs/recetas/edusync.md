# Receta: EduSync - Plataforma Educativa SaaS

> Con 11 bloques Python construyes una plataforma educativa multitenant con IA,
> billing, automation y scheduling. La receta mas compleja del ecosistema ulfblk.

---

## Bloques necesarios

```bash
# Core (los 4 de bot-citas)
uv add ulfblk-core ulfblk-db ulfblk-scheduling ulfblk-calendar

# Auth + Multitenancy
uv add ulfblk-auth ulfblk-multitenant

# Inteligencia + Automatizacion
uv add ulfblk-ai-rag ulfblk-automation ulfblk-notifications

# Billing + Performance
uv add ulfblk-billing ulfblk-redis

# Drivers
uv add aiosqlite cryptography fakeredis
```

## Que obtienes

- FastAPI con create_app() factory, middleware, health check
- Modelos composables: cursos, lecciones, inscripciones, progreso, sesiones en vivo
- Auth JWT con RBAC (admin/instructor/student) via RSA keys
- Multitenancy transparente con TenantContext (PostgreSQL RLS en produccion)
- Scheduling de sesiones en vivo reutilizando AppointmentMixin + AvailabilityMixin
- Tutor IA con RAG pipeline (vector search + LLM sobre contenido de cursos)
- Reglas de automation: progresion de curso, certificaciones automaticas
- Notificaciones multi-canal para recordatorios y certificados
- Billing Stripe: checkout, suscripciones, cancelaciones
- Cache Redis para catalogo de cursos con invalidacion automatica
- Sync de sesiones con calendario (InMemoryCalendarProvider / Google Calendar)

## Arquitectura

```
EduSync Platform
|
|-- Auth Layer (ulfblk-auth + ulfblk-multitenant)
|   |-- JWT con RSA keys
|   |-- RBAC: admin, instructor, student
|   |-- TenantContext: aislamiento por empresa
|
|-- Core (ulfblk-core + ulfblk-db)
|   |-- Modelos: Course, Lesson, Enrollment, Progress
|   |-- CRUD endpoints
|
|-- Scheduling (ulfblk-scheduling + ulfblk-calendar)
|   |-- LiveSession (AppointmentMixin)
|   |-- InstructorAvailability (AvailabilityMixin)
|   |-- generate_slots() + check_conflicts()
|   |-- Calendar sync
|
|-- Smart Layer (ulfblk-ai-rag + ulfblk-automation + ulfblk-notifications)
|   |-- Tutor IA: RAG sobre contenido de cursos
|   |-- RuleEngine: progresion + certificacion
|   |-- Notificaciones de completacion y certificados
|
|-- Business Layer (ulfblk-billing + ulfblk-redis)
    |-- Stripe checkout + suscripciones
    |-- Cache de catalogo con invalidacion
```

## Modelo de dominio

```python
# Auth
EduUser: id, username, role, tenant_id

# Cursos
EduCourse: id, title, description, instructor_id, tenant_id, status
EduLesson: id, course_id, title, content, order, duration_minutes

# Inscripciones
EduEnrollment: id, course_id, student_id, status (active/completed/dropped)
EduProgress: id, enrollment_id, lesson_id, status (not_started/completed), score

# Scheduling (reutiliza mixins de ulfblk-scheduling)
EduLiveSession: AppointmentMixin + course_id, instructor_id, meet_url
EduInstructorAvailability: AvailabilityMixin + resource_id = instructor_id
```

## Roles y permisos

| Accion | student | instructor | admin |
|--------|---------|------------|-------|
| Ver catalogo de cursos | SI | SI | SI |
| Inscribirse | SI | SI | SI |
| Crear curso | NO | SI | SI |
| Listar usuarios | NO | NO | SI |
| Crear checkout | NO | NO | SI |

## Reglas de automation

```yaml
curso-completion:
  condicion: todas las lecciones completadas
  accion: marcar enrollment como "completed" + notificar

certificate-earned:
  condicion: evaluation_type == "final_exam" AND score >= 80
  accion: notificar certificado ganado
```

## Tests

31 tests E2E en `tests/recipes/edusync/`:

| Fase | Archivo | Tests | Bloques |
|------|---------|-------|---------|
| 1. Core | test_edusync_core.py | 9 | core, db, scheduling, calendar |
| 2. Auth | test_edusync_auth.py | 8 | auth, multitenant |
| 3. Smart | test_edusync_smart.py | 8 | ai-rag, automation, notifications |
| 4. Billing | test_edusync_billing.py | 6 | billing, redis |

```bash
uv run pytest tests/recipes/edusync/ -v
```

## Comparativa con bot-citas

| Dimension | bot-citas | EduSync |
|-----------|-----------|---------|
| Bloques Python | 4 | **11** |
| Modelos | 3 | **7** |
| Endpoints | 10 | **25+** |
| Auth/RBAC | no | **JWT + 3 roles** |
| Multitenant | no | **TenantContext** |
| IA | no | **RAG tutor** |
| Billing | no | **Stripe** |
| Automation | no | **RuleEngine** |
| Cache | no | **Redis** |
| Tests | 23 | **31** |

## Adaptar para tu negocio

### Plataforma de onboarding corporativo
- Agregar tracking de tiempo por leccion
- Gamificacion con puntos y badges via automation rules
- Reportes de progreso por departamento

### Marketplace de cursos
- Agregar modelo Creator con revenue share
- Billing con pagos puntuales + suscripciones
- Reviews y ratings con moderacion

### LMS para escuelas
- Agregar modelo Classroom con multiples instructores
- Calendario academico con periodos y feriados (BlockedSlots)
- Evaluaciones con rubrics y feedback
