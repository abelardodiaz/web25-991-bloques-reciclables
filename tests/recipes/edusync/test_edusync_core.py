"""EduSync Phase 1: Core models and CRUD.

Tests the foundational layer using the same 4 blocks as bot-citas:
  - ulfblk-core: App factory, middleware, health
  - ulfblk-db: SQLAlchemy async, Base, TimestampMixin
  - ulfblk-scheduling: AppointmentMixin, AvailabilityMixin, generate_slots, check_conflicts
  - ulfblk-calendar: InMemoryCalendarProvider

Models: Course, Lesson, Enrollment, Progress, LiveSession, InstructorAvailability
Tests: 10 covering CRUD, enrollment flow, scheduling, and calendar sync.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone

from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ulfblk_core import create_app
from ulfblk_calendar import InMemoryCalendarProvider, EventCreate
from ulfblk_db import (
    Base,
    DatabaseSettings,
    create_async_engine,
    create_session_factory,
    get_db_session,
)
from ulfblk_scheduling import (
    check_conflicts,
    generate_slots,
)
from ulfblk_testing import create_test_client

from tests.recipes.edusync.models import (
    EduCourse,
    EduLesson,
    EduEnrollment,
    EduProgress,
    EduLiveSession,
    EduInstructorAvailability,
)


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
_settings = DatabaseSettings(database_url="sqlite+aiosqlite://")
_engine = create_async_engine(_settings)
SessionLocal = create_session_factory(_engine)
db_dep = get_db_session(SessionLocal)

calendar_provider = InMemoryCalendarProvider()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class CourseCreate(BaseModel):
    title: str
    description: str = ""
    instructor_id: str


class CourseOut(BaseModel):
    id: int
    title: str
    description: str | None
    instructor_id: str
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
    date: str  # YYYY-MM-DD
    time: str  # HH:MM
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


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = create_app(service_name="edusync", version="0.1.0")


# -- Courses --
@app.post("/api/courses", response_model=CourseOut, status_code=201)
async def create_course(body: CourseCreate, db: AsyncSession = Depends(db_dep)):
    course = EduCourse(
        title=body.title,
        description=body.description,
        instructor_id=body.instructor_id,
        status="published",
    )
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return CourseOut(
        id=course.id, title=course.title, description=course.description,
        instructor_id=course.instructor_id, status=course.status,
    )


@app.get("/api/courses", response_model=list[CourseOut])
async def list_courses(db: AsyncSession = Depends(db_dep)):
    result = await db.execute(
        select(EduCourse).where(EduCourse.status == "published").order_by(EduCourse.id)
    )
    courses = result.scalars().all()
    return [
        CourseOut(
            id=c.id, title=c.title, description=c.description,
            instructor_id=c.instructor_id, status=c.status,
        )
        for c in courses
    ]


# -- Lessons --
@app.post("/api/courses/{course_id}/lessons", response_model=LessonOut, status_code=201)
async def add_lesson(course_id: int, body: LessonCreate, db: AsyncSession = Depends(db_dep)):
    result = await db.execute(select(EduCourse).where(EduCourse.id == course_id))
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Course not found.")
    lesson = EduLesson(
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


# -- Enrollments --
@app.post("/api/enrollments", response_model=EnrollmentOut, status_code=201)
async def enroll(body: EnrollmentCreate, db: AsyncSession = Depends(db_dep)):
    result = await db.execute(select(EduCourse).where(EduCourse.id == body.course_id))
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Course not found.")
    # Check duplicate enrollment
    result = await db.execute(
        select(EduEnrollment).where(
            EduEnrollment.course_id == body.course_id,
            EduEnrollment.student_id == body.student_id,
        )
    )
    if result.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="Already enrolled.")
    enrollment = EduEnrollment(
        course_id=body.course_id, student_id=body.student_id, status="active",
    )
    db.add(enrollment)
    await db.commit()
    await db.refresh(enrollment)
    # Create progress records for each lesson
    result = await db.execute(
        select(EduLesson).where(EduLesson.course_id == body.course_id).order_by(EduLesson.order)
    )
    lessons = result.scalars().all()
    for lesson in lessons:
        db.add(EduProgress(
            enrollment_id=enrollment.id, lesson_id=lesson.id, status="not_started",
        ))
    await db.commit()
    return EnrollmentOut(
        id=enrollment.id, course_id=enrollment.course_id,
        student_id=enrollment.student_id, status=enrollment.status,
    )


# -- Progress --
@app.get("/api/enrollments/{enrollment_id}/progress", response_model=list[ProgressOut])
async def get_progress(enrollment_id: int, db: AsyncSession = Depends(db_dep)):
    result = await db.execute(
        select(EduProgress).where(EduProgress.enrollment_id == enrollment_id)
    )
    items = result.scalars().all()
    return [ProgressOut(lesson_id=p.lesson_id, status=p.status, score=p.score) for p in items]


@app.post("/api/enrollments/{enrollment_id}/lessons/{lesson_id}/complete", status_code=200)
async def complete_lesson(enrollment_id: int, lesson_id: int, db: AsyncSession = Depends(db_dep)):
    result = await db.execute(
        select(EduProgress).where(
            EduProgress.enrollment_id == enrollment_id,
            EduProgress.lesson_id == lesson_id,
        )
    )
    progress = result.scalar_one_or_none()
    if progress is None:
        raise HTTPException(status_code=404, detail="Progress not found.")
    progress.status = "completed"
    await db.commit()
    return {"message": "Lesson completed.", "lesson_id": lesson_id}


# -- Live Sessions (scheduling) --
@app.get("/api/sessions/slots/{instructor_id}/{date_str}", response_model=list[SlotOut])
async def get_instructor_slots(instructor_id: str, date_str: str, db: AsyncSession = Depends(db_dep)):
    try:
        target_date = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format.")
    result = await db.execute(
        select(EduInstructorAvailability).where(
            EduInstructorAvailability.day_of_week == target_date.weekday(),
            EduInstructorAvailability.is_active.is_(True),
            EduInstructorAvailability.resource_id == instructor_id,
        )
    )
    availabilities = result.scalars().all()
    result = await db.execute(
        select(EduLiveSession).where(
            EduLiveSession.instructor_id == instructor_id,
            EduLiveSession.status != "cancelled",
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
    # Check conflicts
    result = await db.execute(
        select(EduLiveSession).where(
            EduLiveSession.instructor_id == body.instructor_id,
            EduLiveSession.status != "cancelled",
        )
    )
    existing = result.scalars().all()
    day_existing = [s for s in existing if s.scheduled_at.date() == session_date]
    for s in day_existing:
        if s.scheduled_at.tzinfo is None:
            s.scheduled_at = s.scheduled_at.replace(tzinfo=timezone.utc)
    if check_conflicts(start=scheduled_at, end=end_time, existing_appointments=day_existing):
        raise HTTPException(status_code=409, detail="Session conflicts with existing schedule.")
    session = EduLiveSession(
        course_id=body.course_id,
        instructor_id=body.instructor_id,
        scheduled_at=scheduled_at,
        duration_minutes=body.duration_minutes,
        status="pending",
        meet_url=body.meet_url,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    # Sync to calendar
    await calendar_provider.create_event(EventCreate(
        title=f"EduSync: Live Session",
        start=scheduled_at,
        end=end_time,
        description=f"Instructor: {body.instructor_id}",
    ))
    return SessionOut(
        id=session.id, course_id=session.course_id,
        instructor_id=session.instructor_id,
        scheduled_at=session.scheduled_at,
        duration_minutes=session.duration_minutes,
        status=session.status, meet_url=session.meet_url,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _next_weekday() -> date:
    today = date.today()
    if today.weekday() < 5:
        return today
    days_ahead = 7 - today.weekday()
    return today + timedelta(days=days_ahead)


async def _setup_db():
    """Create tables and seed instructor availability."""
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    # Seed instructor availability Mon-Fri 9-13, 14-18
    async with SessionLocal() as session:
        for dow in range(5):
            session.add(EduInstructorAvailability(
                day_of_week=dow, start_time=time(9, 0), end_time=time(13, 0),
                is_active=True, resource_id="instructor-1",
            ))
            session.add(EduInstructorAvailability(
                day_of_week=dow, start_time=time(14, 0), end_time=time(18, 0),
                is_active=True, resource_id="instructor-1",
            ))
        await session.commit()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
class TestHealth:
    async def test_health(self):
        """EduSync app responds with healthy status."""
        async with create_test_client(app) as client:
            resp = await client.get("/health")
            assert resp.status_code == 200
            data = resp.json()
            assert data["service"] == "edusync"
            assert data["status"] == "healthy"


class TestCourses:
    async def test_create_course(self):
        """POST /api/courses creates a published course."""
        await _setup_db()
        async with create_test_client(app) as client:
            resp = await client.post("/api/courses", json={
                "title": "Python Fundamentals",
                "description": "Learn Python from scratch",
                "instructor_id": "instructor-1",
            })
            assert resp.status_code == 201
            data = resp.json()
            assert data["title"] == "Python Fundamentals"
            assert data["status"] == "published"
            assert data["id"] >= 1

    async def test_list_courses(self):
        """GET /api/courses returns published course catalog."""
        await _setup_db()
        async with create_test_client(app) as client:
            # Create 2 courses
            for title in ["Course A", "Course B"]:
                resp = await client.post("/api/courses", json={
                    "title": title, "instructor_id": "instructor-1",
                })
                assert resp.status_code == 201
            resp = await client.get("/api/courses")
            assert resp.status_code == 200
            data = resp.json()
            assert len(data) == 2
            assert data[0]["title"] == "Course A"


class TestEnrollmentFlow:
    async def test_enroll_and_track_progress(self):
        """Full flow: create course -> add lessons -> enroll -> complete lessons."""
        await _setup_db()
        async with create_test_client(app) as client:
            # Create course
            resp = await client.post("/api/courses", json={
                "title": "FastAPI Course", "instructor_id": "instructor-1",
            })
            course_id = resp.json()["id"]

            # Add 3 lessons
            for i in range(1, 4):
                resp = await client.post(f"/api/courses/{course_id}/lessons", json={
                    "title": f"Lesson {i}", "order": i,
                })
                assert resp.status_code == 201

            # Enroll student
            resp = await client.post("/api/enrollments", json={
                "course_id": course_id, "student_id": "student-1",
            })
            assert resp.status_code == 201
            enrollment_id = resp.json()["id"]
            assert resp.json()["status"] == "active"

            # Check progress (3 lessons, all not_started)
            resp = await client.get(f"/api/enrollments/{enrollment_id}/progress")
            assert resp.status_code == 200
            progress = resp.json()
            assert len(progress) == 3
            assert all(p["status"] == "not_started" for p in progress)

            # Complete lesson 1
            lesson_id = progress[0]["lesson_id"]
            resp = await client.post(
                f"/api/enrollments/{enrollment_id}/lessons/{lesson_id}/complete"
            )
            assert resp.status_code == 200

            # Verify progress updated
            resp = await client.get(f"/api/enrollments/{enrollment_id}/progress")
            progress = resp.json()
            completed = [p for p in progress if p["status"] == "completed"]
            assert len(completed) == 1

    async def test_duplicate_enrollment_returns_409(self):
        """Enrolling twice in same course returns 409."""
        await _setup_db()
        async with create_test_client(app) as client:
            resp = await client.post("/api/courses", json={
                "title": "Test Course", "instructor_id": "instructor-1",
            })
            course_id = resp.json()["id"]
            resp = await client.post("/api/enrollments", json={
                "course_id": course_id, "student_id": "student-1",
            })
            assert resp.status_code == 201
            resp = await client.post("/api/enrollments", json={
                "course_id": course_id, "student_id": "student-1",
            })
            assert resp.status_code == 409

    async def test_enroll_nonexistent_course_returns_404(self):
        """Enrolling in a nonexistent course returns 404."""
        await _setup_db()
        async with create_test_client(app) as client:
            resp = await client.post("/api/enrollments", json={
                "course_id": 9999, "student_id": "student-1",
            })
            assert resp.status_code == 404


class TestScheduling:
    async def test_instructor_slots(self):
        """GET slots returns available time slots for an instructor."""
        await _setup_db()
        target = _next_weekday()
        async with create_test_client(app) as client:
            resp = await client.get(
                f"/api/sessions/slots/instructor-1/{target.isoformat()}"
            )
            assert resp.status_code == 200
            data = resp.json()
            assert isinstance(data, list)
            assert len(data) > 0
            assert data[0]["available"] is True

    async def test_create_live_session(self):
        """POST /api/sessions creates a live session with calendar sync."""
        await _setup_db()
        calendar_provider._events.clear()
        target = _next_weekday()
        async with create_test_client(app) as client:
            resp = await client.post("/api/courses", json={
                "title": "Live Course", "instructor_id": "instructor-1",
            })
            course_id = resp.json()["id"]
            resp = await client.post("/api/sessions", json={
                "course_id": course_id,
                "instructor_id": "instructor-1",
                "date": target.isoformat(),
                "time": "10:00",
                "duration_minutes": 60,
                "meet_url": "https://meet.example.com/abc",
            })
            assert resp.status_code == 201
            data = resp.json()
            assert data["instructor_id"] == "instructor-1"
            assert data["duration_minutes"] == 60
            assert data["status"] == "pending"
            assert data["meet_url"] == "https://meet.example.com/abc"
        # Verify calendar sync
        day_start = datetime.combine(target, time(0, 0), tzinfo=timezone.utc)
        day_end = datetime.combine(target, time(23, 59), tzinfo=timezone.utc)
        events = await calendar_provider.list_events(start=day_start, end=day_end)
        assert len(events) == 1
        assert "Live Session" in events[0].title

    async def test_session_conflict(self):
        """Double-booking same instructor at same time returns 409."""
        await _setup_db()
        target = _next_weekday()
        async with create_test_client(app) as client:
            resp = await client.post("/api/courses", json={
                "title": "Course X", "instructor_id": "instructor-1",
            })
            course_id = resp.json()["id"]
            # First session
            resp = await client.post("/api/sessions", json={
                "course_id": course_id, "instructor_id": "instructor-1",
                "date": target.isoformat(), "time": "11:00", "duration_minutes": 60,
            })
            assert resp.status_code == 201
            # Conflicting session
            resp = await client.post("/api/sessions", json={
                "course_id": course_id, "instructor_id": "instructor-1",
                "date": target.isoformat(), "time": "11:30", "duration_minutes": 60,
            })
            assert resp.status_code == 409
            assert "conflict" in resp.json()["detail"].lower()
