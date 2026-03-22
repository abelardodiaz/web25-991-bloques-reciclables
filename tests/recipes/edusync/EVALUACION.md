# Evaluacion: Receta EduSync - Plataforma Educativa

> Evaluacion pre-implementacion. Objetivo: validar que los bloques ulfblk
> soportan esta receta antes de escribir una sola linea de codigo.

## Idea original (DeepSeek ticket #784)

SaaS para capacitacion corporativa: aulas virtuales, instructores, cursos,
evaluaciones con IA, certificaciones automaticas y billing por empresa.
Propuso 13 Python + 6 TS = 19 bloques.

## Evaluacion de viabilidad por bloque

### Inventario real de bloques (auditado)

| Bloque | Estado | Tests | Listo? |
|--------|--------|-------|--------|
| ulfblk-core | Implementado | Si | SI |
| ulfblk-db | Implementado | Si | SI |
| ulfblk-auth | Implementado (JWT, RBAC, brute force, encryption) | 10 | SI |
| ulfblk-multitenant | Implementado (TenantContext, RLS) | 8 | SI |
| ulfblk-scheduling | Implementado (Appointments, Slots, Conflicts) | 51 | SI |
| ulfblk-calendar | Implementado (InMemory, Google) | 36 | SI |
| ulfblk-notifications | Implementado (Console, Webhook, Templates) | 41 | SI |
| ulfblk-channels | Implementado (Email, Telegram, WhatsApp) | 34 | SI |
| ulfblk-ai-rag | Implementado (ChromaDB, Ollama, OpenAI) | 47 | SI |
| ulfblk-automation | Implementado (RuleEngine, Conditions, Actions) | 65 | SI |
| ulfblk-billing | Implementado (Stripe, Subscriptions, Webhooks) | 81 | SI |
| ulfblk-gateway | Implementado (CircuitBreaker, RateLimiter, Proxy) | 33 | SI |
| ulfblk-redis | Implementado (Cache, Streams, Pub/Sub) | 34 | SI |
| ulfblk-testing | Implementado (TestClient, fixtures) | Si | SI |
| @ulfblk/admin | Implementado (react-admin DataProvider) | Si | SI |
| @ulfblk/api-client | Implementado (HTTP + paginacion) | Si | SI |
| @ulfblk/calendar-ui | Implementado (DaySelector, SlotPicker) | Si | SI |
| @ulfblk/chat-ui | **Scaffolded** (solo useChat hook + types) | 0 | **NO** |
| @ulfblk/forms | Implementado | Si | SI |
| @ulfblk/dashboard | **Scaffolded** (solo hooks utilities) | 0 | **NO** |
| @ulfblk/auth-react | Implementado (useAuth, guards, JWT) | Si | SI |
| @ulfblk/types | Implementado | Si | SI |
| @ulfblk/ui | Implementado (Tailwind preset, tokens) | Si | SI |

### Bloques descartados de la propuesta original

| Bloque | Razon de descarte |
|--------|-------------------|
| @ulfblk/chat-ui | Scaffolded, 0 tests. No se puede usar en una receta de referencia. |
| @ulfblk/dashboard | Scaffolded, 0 tests. Solo tiene hooks utilitarios, no componentes. |
| ulfblk-gateway | Util para infra pero no para logica de negocio educativa. Forzarlo seria artificial. |
| ulfblk-channels | Overlap con notifications. En una plataforma educativa, notifications cubre el caso. Channels es para recibir mensajes de WhatsApp/Telegram, no para enviar - no aplica aqui. |

### Bloques que SI aplican (con justificacion)

#### Backend Python (11 bloques)

| # | Bloque | Rol en EduSync | Justificacion |
|---|--------|----------------|---------------|
| 1 | ulfblk-core | App factory, middleware, health | Base obligatoria |
| 2 | ulfblk-db | Modelos: Course, Lesson, Enrollment, Progress, Evaluation | Persistencia |
| 3 | ulfblk-auth | JWT login, RBAC (admin/instructor/student) | Roles son core del dominio |
| 4 | ulfblk-multitenant | Empresas clientes aisladas con RLS | SaaS B2B real |
| 5 | ulfblk-scheduling | Sesiones en vivo, horarios de instructores | Reutiliza todo bot-citas |
| 6 | ulfblk-calendar | Sync de sesiones con Google Calendar | Instructores ven en su calendar |
| 7 | ulfblk-notifications | Recordatorios de clase, nuevos cursos, evaluaciones | Multi-canal (console+webhook) |
| 8 | ulfblk-ai-rag | Tutor IA: estudiantes preguntan sobre contenido del curso | RAG sobre material del curso |
| 9 | ulfblk-automation | Reglas: completar leccion -> desbloquear siguiente, nota >= 80 -> certificar | Progresion automatica |
| 10 | ulfblk-billing | Suscripciones empresariales Stripe | Monetizacion SaaS |
| 11 | ulfblk-redis | Cache de catalogo, sesiones activas, progreso en tiempo real | Performance |

#### Frontend TypeScript (6 bloques)

| # | Bloque | Rol en EduSync |
|---|--------|----------------|
| 1 | @ulfblk/admin | Panel admin: gestionar cursos, instructores, empresas |
| 2 | @ulfblk/api-client | HTTP client para todas las llamadas al backend |
| 3 | @ulfblk/calendar-ui | Calendario de sesiones en vivo |
| 4 | @ulfblk/forms | Formularios de evaluacion, inscripcion, perfil |
| 5 | @ulfblk/auth-react | Login, guards por rol, AuthProvider |
| 6 | @ulfblk/ui | Design system base para toda la UI |

**Total: 17 bloques (11 Python + 6 TS)**

## Modelo de dominio

```
Course
  id, title, description, instructor_id, tenant_id
  status: draft | published | archived

Lesson
  id, course_id, title, content, order, duration_minutes

Enrollment
  id, course_id, student_id, tenant_id
  status: active | completed | dropped
  enrolled_at, completed_at

Progress
  id, enrollment_id, lesson_id
  status: not_started | in_progress | completed
  score (nullable), completed_at

Evaluation (reusa AppointmentMixin? no - modelo propio)
  id, enrollment_id, lesson_id
  type: quiz | assignment | final_exam
  score, max_score, submitted_at

-- Reutilizados de scheduling --
Session (= Appointment)
  id, course_id, instructor_id
  scheduled_at, duration_minutes, status
  + meet_url (campo custom)

InstructorAvailability (= Availability)
  day_of_week, start_time, end_time, instructor_id (= resource_id)

-- Reutilizados de billing --
Subscription (Stripe via ulfblk-billing)
  empresa -> plan (basic/pro/enterprise)

-- Reutilizados de auth --
User (con RBAC)
  roles: admin | instructor | student
```

## Endpoints planificados

### Publicos (sin auth)
| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | /health | Health check |
| POST | /auth/login | Login JWT |
| POST | /auth/register | Registro estudiante |

### Estudiante (RequireAuth)
| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | /api/courses | Catalogo de cursos |
| GET | /api/courses/{id} | Detalle de curso con lecciones |
| POST | /api/enrollments | Inscribirse a un curso |
| GET | /api/enrollments | Mis cursos |
| GET | /api/progress/{enrollment_id} | Mi progreso en un curso |
| POST | /api/progress/{enrollment_id}/lessons/{lesson_id}/complete | Marcar leccion completada |
| POST | /api/evaluations | Enviar evaluacion |
| GET | /api/sessions/{date} | Sesiones disponibles |
| POST | /api/chat | Preguntar al tutor IA sobre contenido |

### Instructor (RequireRole: instructor)
| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | /api/instructor/courses | Mis cursos |
| POST | /api/instructor/courses | Crear curso |
| PUT | /api/instructor/courses/{id} | Editar curso |
| POST | /api/instructor/courses/{id}/lessons | Agregar leccion |
| GET | /api/instructor/sessions | Mis sesiones |
| GET | /api/instructor/availability | Mi disponibilidad |

### Admin (RequireRole: admin)
| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | /api/admin/users | Listar usuarios |
| GET | /api/admin/stats | Dashboard stats |
| GET | /api/admin/enrollments | Todas las inscripciones |
| POST | /api/admin/billing/checkout | Crear checkout Stripe |

### React-admin (panel)
| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET/PUT/POST/DELETE | /api/courses/* | CRUD cursos |
| GET/PUT | /api/enrollments/* | CRUD inscripciones |
| GET | /api/availabilities | Disponibilidades |

## Flujos de automation (RuleEngine)

```yaml
regla: "Completar leccion -> desbloquear siguiente"
  condicion: progress.status == "completed"
  accion: set next_lesson.status = "in_progress"

regla: "Completar todas las lecciones -> marcar curso completado"
  condicion: all_lessons_completed == true
  accion: set enrollment.status = "completed"

regla: "Score >= 80 en final_exam -> emitir certificado"
  condicion: evaluation.type == "final_exam" AND evaluation.score >= 80
  accion: notify(student, "certificate_ready")

regla: "Sesion en 1 hora -> recordatorio"
  condicion: session.scheduled_at - now <= 1h
  accion: notify(student, "session_reminder")
```

## Plan de tests (lo que se debe probar)

### Fase 1: Core (modelos + CRUD basico)
- Health check
- Crear curso con lecciones
- Inscripcion de estudiante
- Progreso: completar lecciones una por una
- Evaluaciones con score

### Fase 2: Scheduling (sesiones en vivo)
- Disponibilidad de instructor (reutiliza AvailabilityMixin)
- Generar slots de sesiones
- Reservar sesion (reutiliza AppointmentMixin)
- Conflictos de sesion

### Fase 3: Auth + RBAC
- Login devuelve JWT con roles
- Estudiante no puede crear cursos
- Instructor no puede ver billing
- Admin puede todo

### Fase 4: Integraciones avanzadas
- AI Tutor: pregunta sobre contenido -> RAG responde
- Automation: completar leccion -> desbloquea siguiente
- Notifications: recordatorio de sesion
- Billing: crear checkout Stripe
- Redis: cache de catalogo
- Calendar: sync de sesion
- Multitenant: datos aislados entre empresas

## Comparativa con bot-citas

| Dimension | bot-citas | EduSync |
|-----------|-----------|---------|
| Bloques Python | 4 | 11 |
| Bloques TS | 4 | 6 |
| Total | 8 | **17** |
| Modelos de dominio | 3 | 8+ |
| Endpoints | 10 | 25+ |
| Roles | ninguno | 3 (admin/instructor/student) |
| Auth | ninguna | JWT + RBAC |
| Multitenant | no | si (RLS) |
| IA | no | RAG tutor |
| Billing | no | Stripe |
| Automation | no | RuleEngine |
| Cache | no | Redis |
| Tests estimados | 23 | 40-60 |
| Complejidad relativa | 1x | ~5x |

## Riesgos y mitigaciones

| Riesgo | Mitigacion |
|--------|------------|
| Demasiado grande para un solo test file | Dividir en fases (4 archivos de test) |
| AI RAG necesita ChromaDB corriendo | Usar mocks/fakes en tests |
| Billing necesita Stripe keys | StripeProvider acepta test keys, usar mocks |
| Redis necesita server | Tests usan FakeRedis o mock del CacheStore |
| Multitenant necesita PostgreSQL RLS | Tests con SQLite validan TenantContext logic, no RLS real |
| Scope creep | Fase 1 y 2 son el MVP minimo. Fases 3-4 agregan bloques incrementalmente |

## Decision

**VIABLE.** Los 17 bloques estan implementados con tests. La receta demuestra
composabilidad real porque cada bloque resuelve un problema concreto del dominio
educativo, no esta forzado.

**Siguiente paso:** Implementar Fase 1 (modelos + CRUD) como test standalone,
igual que bot-citas. Despues agregar fases incrementalmente.
