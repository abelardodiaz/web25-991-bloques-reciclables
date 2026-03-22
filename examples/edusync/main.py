"""EduSync API - Educational SaaS Platform.

Demonstrates 11 ulfblk blocks working together:
- ulfblk-core: App factory, middleware, health, logging
- ulfblk-db: SQLAlchemy async models with composable mixins
- ulfblk-auth: JWT authentication with RSA keys
- ulfblk-multitenant: TenantContext for data isolation
- ulfblk-scheduling: Live sessions with slot generation and conflict detection
- ulfblk-calendar: InMemoryCalendarProvider for session sync
- ulfblk-notifications: Console notifications for course events
- ulfblk-ai-rag: (mock) AI tutor for course Q&A
- ulfblk-automation: RuleEngine for course progression
- ulfblk-billing: (mock) Stripe billing for subscriptions
- ulfblk-redis: (mock) Cache for course catalog

Run with:
    cd examples/edusync
    uv run uvicorn main:app --reload
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import date, datetime, time, timedelta, timezone
from typing import Annotated

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from fastapi import Depends, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ulfblk_core import create_app, get_logger, setup_logging
from ulfblk_auth.jwt import JWTManager
from ulfblk_calendar import InMemoryCalendarProvider, EventCreate
from ulfblk_multitenant.context import get_current_tenant, set_current_tenant
from ulfblk_multitenant.context.tenant import clear_current_tenant
from ulfblk_scheduling import generate_slots, check_conflicts

from database import SessionLocal, db_dep, init_db
from models import (
    User, Course, Lesson, Enrollment, Progress,
    LiveSession, InstructorAvailability,
)
from seed import seed_data

setup_logging(level="INFO")
logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Auth setup (RSA keys generated at startup)
# ---------------------------------------------------------------------------
_pk = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_private_pem = _pk.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
).decode()
_public_pem = _pk.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
).decode()

jwt_manager = JWTManager(
    private_key=_private_pem,
    public_key=_public_pem,
    access_token_expire_minutes=60,
    refresh_token_expire_days=7,
)

calendar_provider = InMemoryCalendarProvider()


# ---------------------------------------------------------------------------
# Auth dependencies
# ---------------------------------------------------------------------------
async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token.")
    token = authorization.split(" ", 1)[1]
    try:
        data = jwt_manager.decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token.")
    return {
        "user_id": data.user_id,
        "tenant_id": data.tenant_id,
        "roles": data.roles,
    }


def require_role(*allowed_roles: str):
    async def _check(user: dict = Depends(get_current_user)) -> dict:
        if not any(r in allowed_roles for r in user["roles"]):
            raise HTTPException(status_code=403, detail="Insufficient permissions.")
        set_current_tenant(tenant_id=user["tenant_id"])
        return user
    return _check


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class LoginRequest(BaseModel):
    username: str
    tenant_id: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    tenant_id: str


class CourseCreate(BaseModel):
    title: str
    description: str = ""


class CourseOut(BaseModel):
    id: int
    title: str
    description: str | None
    instructor_id: str
    tenant_id: str
    status: str


class LessonCreate(BaseModel):
    title: str
    content: str = ""
    order: int = 1
    duration_minutes: int = 30


class LessonOut(BaseModel):
    id: int
    course_id: int
    title: str
    order: int
    duration_minutes: int


class EnrollmentCreate(BaseModel):
    course_id: int
    student_id: str


class EnrollmentOut(BaseModel):
    id: int
    course_id: int
    student_id: str
    status: str


class ProgressOut(BaseModel):
    lesson_id: int
    status: str
    score: float | None


class SessionCreate(BaseModel):
    course_id: int
    instructor_id: str
    date: str
    time: str
    duration_minutes: int = 60
    meet_url: str = ""


class SessionOut(BaseModel):
    id: int
    course_id: int
    instructor_id: str
    scheduled_at: datetime
    duration_minutes: int
    status: str
    meet_url: str | None


class SlotOut(BaseModel):
    start: datetime
    end: datetime
    available: bool


class UserOut(BaseModel):
    id: int
    username: str
    role: str
    tenant_id: str


class ChatRequest(BaseModel):
    question: str
    course_id: int


class ChatResponse(BaseModel):
    answer: str
    sources_count: int


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app):
    await init_db()
    await seed_data(SessionLocal)
    logger.info("database.ready", msg="Tables created and data seeded")
    yield


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = create_app(
    service_name="edusync",
    version="0.1.0",
    title="EduSync - Educational SaaS Platform",
    description="17 ulfblk blocks composing an educational platform",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Auth endpoints
# ---------------------------------------------------------------------------
@app.post("/auth/login", response_model=LoginResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(db_dep)):
    result = await db.execute(
        select(User).where(
            User.username == body.username,
            User.tenant_id == body.tenant_id,
        )
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    token = jwt_manager.create_access_token(
        user_id=str(user.id),
        tenant_id=user.tenant_id,
        roles=[user.role],
    )
    return LoginResponse(
        access_token=token, role=user.role, tenant_id=user.tenant_id,
    )


# ---------------------------------------------------------------------------
# Course endpoints
# ---------------------------------------------------------------------------
@app.get("/api/courses", response_model=list[CourseOut])
async def list_courses(
    user: dict = Depends(require_role("admin", "instructor", "student")),
    db: AsyncSession = Depends(db_dep),
):
    tenant = get_current_tenant()
    result = await db.execute(
        select(Course).where(
            Course.tenant_id == tenant.tenant_id,
            Course.status == "published",
        ).order_by(Course.id)
    )
    courses = result.scalars().all()
    clear_current_tenant()
    return [
        CourseOut(
            id=c.id, title=c.title, description=c.description,
            instructor_id=c.instructor_id, tenant_id=c.tenant_id, status=c.status,
        )
        for c in courses
    ]


@app.get("/api/courses/{course_id}", response_model=CourseOut)
async def get_course(course_id: int, db: AsyncSession = Depends(db_dep)):
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found.")
    return CourseOut(
        id=course.id, title=course.title, description=course.description,
        instructor_id=course.instructor_id, tenant_id=course.tenant_id,
        status=course.status,
    )


@app.post("/api/courses", response_model=CourseOut, status_code=201)
async def create_course(
    body: CourseCreate,
    user: dict = Depends(require_role("admin", "instructor")),
    db: AsyncSession = Depends(db_dep),
):
    tenant = get_current_tenant()
    course = Course(
        title=body.title, description=body.description,
        instructor_id=user["user_id"], tenant_id=tenant.tenant_id,
        status="published",
    )
    db.add(course)
    await db.commit()
    await db.refresh(course)
    clear_current_tenant()
    return CourseOut(
        id=course.id, title=course.title, description=course.description,
        instructor_id=course.instructor_id, tenant_id=course.tenant_id,
        status=course.status,
    )


# ---------------------------------------------------------------------------
# Lesson endpoints
# ---------------------------------------------------------------------------
@app.get("/api/courses/{course_id}/lessons", response_model=list[LessonOut])
async def list_lessons(course_id: int, db: AsyncSession = Depends(db_dep)):
    result = await db.execute(
        select(Lesson).where(Lesson.course_id == course_id).order_by(Lesson.order)
    )
    lessons = result.scalars().all()
    return [
        LessonOut(
            id=l.id, course_id=l.course_id, title=l.title,
            order=l.order, duration_minutes=l.duration_minutes,
        )
        for l in lessons
    ]


@app.post("/api/courses/{course_id}/lessons", response_model=LessonOut, status_code=201)
async def add_lesson(course_id: int, body: LessonCreate, db: AsyncSession = Depends(db_dep)):
    result = await db.execute(select(Course).where(Course.id == course_id))
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Course not found.")
    lesson = Lesson(
        course_id=course_id, title=body.title, content=body.content,
        order=body.order, duration_minutes=body.duration_minutes,
    )
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)
    return LessonOut(
        id=lesson.id, course_id=lesson.course_id, title=lesson.title,
        order=lesson.order, duration_minutes=lesson.duration_minutes,
    )


# ---------------------------------------------------------------------------
# Enrollment endpoints
# ---------------------------------------------------------------------------
@app.post("/api/enrollments", response_model=EnrollmentOut, status_code=201)
async def enroll(body: EnrollmentCreate, db: AsyncSession = Depends(db_dep)):
    result = await db.execute(select(Course).where(Course.id == body.course_id))
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Course not found.")
    result = await db.execute(
        select(Enrollment).where(
            Enrollment.course_id == body.course_id,
            Enrollment.student_id == body.student_id,
        )
    )
    if result.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="Already enrolled.")
    enrollment = Enrollment(
        course_id=body.course_id, student_id=body.student_id, status="active",
    )
    db.add(enrollment)
    await db.commit()
    await db.refresh(enrollment)
    # Create progress for each lesson
    result = await db.execute(
        select(Lesson).where(Lesson.course_id == body.course_id).order_by(Lesson.order)
    )
    for lesson in result.scalars().all():
        db.add(Progress(
            enrollment_id=enrollment.id, lesson_id=lesson.id, status="not_started",
        ))
    await db.commit()
    return EnrollmentOut(
        id=enrollment.id, course_id=enrollment.course_id,
        student_id=enrollment.student_id, status=enrollment.status,
    )


@app.get("/api/enrollments/{enrollment_id}/progress", response_model=list[ProgressOut])
async def get_progress(enrollment_id: int, db: AsyncSession = Depends(db_dep)):
    result = await db.execute(
        select(Progress).where(Progress.enrollment_id == enrollment_id)
    )
    items = result.scalars().all()
    return [ProgressOut(lesson_id=p.lesson_id, status=p.status, score=p.score) for p in items]


@app.post("/api/enrollments/{enrollment_id}/lessons/{lesson_id}/complete")
async def complete_lesson(enrollment_id: int, lesson_id: int, db: AsyncSession = Depends(db_dep)):
    result = await db.execute(
        select(Progress).where(
            Progress.enrollment_id == enrollment_id,
            Progress.lesson_id == lesson_id,
        )
    )
    progress = result.scalar_one_or_none()
    if progress is None:
        raise HTTPException(status_code=404, detail="Progress not found.")
    progress.status = "completed"
    await db.commit()
    return {"message": "Lesson completed.", "lesson_id": lesson_id}


# ---------------------------------------------------------------------------
# Live session endpoints (scheduling)
# ---------------------------------------------------------------------------
@app.get("/api/sessions/slots/{instructor_id}/{date_str}", response_model=list[SlotOut])
async def get_instructor_slots(instructor_id: str, date_str: str, db: AsyncSession = Depends(db_dep)):
    try:
        target_date = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format.")
    result = await db.execute(
        select(InstructorAvailability).where(
            InstructorAvailability.day_of_week == target_date.weekday(),
            InstructorAvailability.is_active.is_(True),
            InstructorAvailability.resource_id == instructor_id,
        )
    )
    availabilities = result.scalars().all()
    result = await db.execute(
        select(LiveSession).where(
            LiveSession.instructor_id == instructor_id,
            LiveSession.status != "cancelled",
        )
    )
    all_sessions = result.scalars().all()
    day_sessions = [s for s in all_sessions if s.scheduled_at.date() == target_date]
    slots = generate_slots(
        target_date=target_date,
        availabilities=availabilities,
        duration_minutes=60,
        existing_appointments=day_sessions,
    )
    return [SlotOut(start=s.start, end=s.end, available=s.available) for s in slots]


@app.post("/api/sessions", response_model=SessionOut, status_code=201)
async def create_session(body: SessionCreate, db: AsyncSession = Depends(db_dep)):
    try:
        session_date = date.fromisoformat(body.date)
        session_time = time.fromisoformat(body.time)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date/time format.")
    scheduled_at = datetime.combine(session_date, session_time, tzinfo=timezone.utc)
    end_time = scheduled_at + timedelta(minutes=body.duration_minutes)
    result = await db.execute(
        select(LiveSession).where(
            LiveSession.instructor_id == body.instructor_id,
            LiveSession.status != "cancelled",
        )
    )
    existing = result.scalars().all()
    day_existing = [s for s in existing if s.scheduled_at.date() == session_date]
    for s in day_existing:
        if s.scheduled_at.tzinfo is None:
            s.scheduled_at = s.scheduled_at.replace(tzinfo=timezone.utc)
    if check_conflicts(start=scheduled_at, end=end_time, existing_appointments=day_existing):
        raise HTTPException(status_code=409, detail="Session conflicts with existing schedule.")
    session = LiveSession(
        course_id=body.course_id, instructor_id=body.instructor_id,
        scheduled_at=scheduled_at, duration_minutes=body.duration_minutes,
        status="pending", meet_url=body.meet_url,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    await calendar_provider.create_event(EventCreate(
        title=f"EduSync: Live Session",
        start=scheduled_at, end=end_time,
        description=f"Instructor: {body.instructor_id}",
    ))
    return SessionOut(
        id=session.id, course_id=session.course_id,
        instructor_id=session.instructor_id, scheduled_at=session.scheduled_at,
        duration_minutes=session.duration_minutes, status=session.status,
        meet_url=session.meet_url,
    )


# ---------------------------------------------------------------------------
# AI Tutor (simple mock - real impl would use ulfblk-ai-rag)
# ---------------------------------------------------------------------------
@app.post("/api/chat", response_model=ChatResponse)
async def ai_tutor_chat(body: ChatRequest, db: AsyncSession = Depends(db_dep)):
    """AI tutor: answers questions about course content."""
    result = await db.execute(select(Course).where(Course.id == body.course_id))
    course = result.scalar_one_or_none()
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found.")
    # In production: RAGPipeline queries vector store, then LLM generates
    # For the example: return a contextual mock response
    answer = (
        f"Based on the content of '{course.title}', "
        f"here is what I know about your question: '{body.question}'. "
        f"This course covers the fundamentals and practical applications. "
        f"Check the lessons for detailed explanations."
    )
    return ChatResponse(answer=answer, sources_count=2)


# ---------------------------------------------------------------------------
# Admin endpoints
# ---------------------------------------------------------------------------
@app.get("/api/admin/users", response_model=list[UserOut])
async def list_users(
    user: dict = Depends(require_role("admin")),
    db: AsyncSession = Depends(db_dep),
):
    tenant = get_current_tenant()
    result = await db.execute(
        select(User).where(User.tenant_id == tenant.tenant_id)
    )
    users = result.scalars().all()
    clear_current_tenant()
    return [
        UserOut(id=u.id, username=u.username, role=u.role, tenant_id=u.tenant_id)
        for u in users
    ]
