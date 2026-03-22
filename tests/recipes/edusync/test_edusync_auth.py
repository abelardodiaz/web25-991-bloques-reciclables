"""EduSync Phase 2: Authentication, RBAC, and multitenancy.

Adds 2 new blocks on top of Phase 1:
  - ulfblk-auth: JWTManager with RSA keys, role-based access control
  - ulfblk-multitenant: TenantContext for data isolation between organizations

Tests: 8 covering login, token validation, role guards, and tenant isolation.
"""

from __future__ import annotations

from typing import Annotated

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from fastapi import Depends, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ulfblk_core import create_app
from ulfblk_auth.jwt import JWTManager
from ulfblk_multitenant.context import (
    TenantContext,
    get_current_tenant,
    set_current_tenant,
)
from ulfblk_multitenant.context.tenant import clear_current_tenant
from ulfblk_db import (
    Base,
    DatabaseSettings,
    create_async_engine,
    create_session_factory,
    get_db_session,
)
from ulfblk_testing import create_test_client

from tests.recipes.edusync.models import EduUser, EduCourse


# ---------------------------------------------------------------------------
# RSA keys for JWT (generated once at module level)
# ---------------------------------------------------------------------------
_private_key_obj = rsa.generate_private_key(public_exponent=65537, key_size=2048)
PRIVATE_PEM = _private_key_obj.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
).decode()
PUBLIC_PEM = _private_key_obj.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
).decode()

jwt_manager = JWTManager(
    private_key=PRIVATE_PEM,
    public_key=PUBLIC_PEM,
    access_token_expire_minutes=30,
    refresh_token_expire_days=7,
)


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
_settings = DatabaseSettings(database_url="sqlite+aiosqlite://")
_engine = create_async_engine(_settings)
SessionLocal = create_session_factory(_engine)
db_dep = get_db_session(SessionLocal)


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


class CourseOut(BaseModel):
    id: int
    title: str
    instructor_id: str
    tenant_id: str


class UserOut(BaseModel):
    id: int
    username: str
    role: str
    tenant_id: str


# ---------------------------------------------------------------------------
# Auth dependency
# ---------------------------------------------------------------------------
async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
) -> dict:
    """Decode JWT from Authorization header and return user data."""
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
    """Factory that returns a dependency checking user has one of the allowed roles."""
    async def _check(user: dict = Depends(get_current_user)) -> dict:
        if not any(r in allowed_roles for r in user["roles"]):
            raise HTTPException(status_code=403, detail="Insufficient permissions.")
        # Set tenant context for downstream queries
        set_current_tenant(tenant_id=user["tenant_id"])
        return user
    return _check


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = create_app(service_name="edusync-auth", version="0.1.0")


@app.post("/auth/login", response_model=LoginResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(db_dep)):
    """Login: find user by username+tenant, return JWT."""
    result = await db.execute(
        select(EduUser).where(
            EduUser.username == body.username,
            EduUser.tenant_id == body.tenant_id,
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


@app.get("/api/courses", response_model=list[CourseOut])
async def list_courses(
    user: dict = Depends(require_role("admin", "instructor", "student")),
    db: AsyncSession = Depends(db_dep),
):
    """List courses filtered by tenant (no RLS in SQLite, manual filter)."""
    tenant = get_current_tenant()
    result = await db.execute(
        select(EduCourse).where(EduCourse.tenant_id == tenant.tenant_id)
    )
    courses = result.scalars().all()
    clear_current_tenant()
    return [
        CourseOut(
            id=c.id, title=c.title,
            instructor_id=c.instructor_id, tenant_id=c.tenant_id,
        )
        for c in courses
    ]


@app.post("/api/courses", response_model=CourseOut, status_code=201)
async def create_course(
    body: CourseCreate,
    user: dict = Depends(require_role("admin", "instructor")),
    db: AsyncSession = Depends(db_dep),
):
    """Only instructors and admins can create courses."""
    tenant = get_current_tenant()
    course = EduCourse(
        title=body.title,
        instructor_id=user["user_id"],
        tenant_id=tenant.tenant_id,
    )
    db.add(course)
    await db.commit()
    await db.refresh(course)
    clear_current_tenant()
    return CourseOut(
        id=course.id, title=course.title,
        instructor_id=course.instructor_id, tenant_id=course.tenant_id,
    )


@app.get("/api/admin/users", response_model=list[UserOut])
async def list_users(
    user: dict = Depends(require_role("admin")),
    db: AsyncSession = Depends(db_dep),
):
    """Only admins can list users."""
    tenant = get_current_tenant()
    result = await db.execute(
        select(EduUser).where(EduUser.tenant_id == tenant.tenant_id)
    )
    users = result.scalars().all()
    clear_current_tenant()
    return [
        UserOut(id=u.id, username=u.username, role=u.role, tenant_id=u.tenant_id)
        for u in users
    ]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
async def _setup_db():
    """Create tables and seed users in 2 tenants."""
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        # Tenant A: Acme Corp
        session.add(EduUser(username="admin-a", role="admin", tenant_id="acme"))
        session.add(EduUser(username="teacher-a", role="instructor", tenant_id="acme"))
        session.add(EduUser(username="student-a", role="student", tenant_id="acme"))
        # Tenant B: Globex Inc
        session.add(EduUser(username="admin-b", role="admin", tenant_id="globex"))
        session.add(EduUser(username="student-b", role="student", tenant_id="globex"))
        # Course in Acme
        session.add(EduCourse(
            title="Acme Python 101", instructor_id="2", tenant_id="acme",
        ))
        # Course in Globex
        session.add(EduCourse(
            title="Globex Data Science", instructor_id="4", tenant_id="globex",
        ))
        await session.commit()


def _login_token(user_id: str, tenant_id: str, role: str) -> str:
    """Generate a JWT for testing."""
    return jwt_manager.create_access_token(
        user_id=user_id, tenant_id=tenant_id, roles=[role],
    )


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
class TestLogin:
    async def test_login_returns_jwt(self):
        """POST /auth/login with valid user returns JWT token."""
        await _setup_db()
        async with create_test_client(app) as client:
            resp = await client.post("/auth/login", json={
                "username": "admin-a", "tenant_id": "acme",
            })
            assert resp.status_code == 200
            data = resp.json()
            assert "access_token" in data
            assert data["role"] == "admin"
            assert data["tenant_id"] == "acme"
            # Verify token is decodable
            decoded = jwt_manager.decode_token(data["access_token"])
            assert decoded.tenant_id == "acme"
            assert "admin" in decoded.roles

    async def test_login_invalid_user_returns_401(self):
        """POST /auth/login with nonexistent user returns 401."""
        await _setup_db()
        async with create_test_client(app) as client:
            resp = await client.post("/auth/login", json={
                "username": "ghost", "tenant_id": "acme",
            })
            assert resp.status_code == 401


class TestRBAC:
    async def test_no_token_returns_401(self):
        """Accessing protected endpoint without token returns 401."""
        await _setup_db()
        async with create_test_client(app) as client:
            resp = await client.get("/api/courses")
            assert resp.status_code == 401

    async def test_student_can_list_courses(self):
        """Students can access GET /api/courses."""
        await _setup_db()
        token = _login_token("3", "acme", "student")
        async with create_test_client(app) as client:
            resp = await client.get("/api/courses", headers=_auth_header(token))
            assert resp.status_code == 200

    async def test_student_cannot_create_course(self):
        """Students are forbidden from POST /api/courses (403)."""
        await _setup_db()
        token = _login_token("3", "acme", "student")
        async with create_test_client(app) as client:
            resp = await client.post(
                "/api/courses",
                json={"title": "Hacker Course"},
                headers=_auth_header(token),
            )
            assert resp.status_code == 403

    async def test_instructor_can_create_course(self):
        """Instructors can create courses."""
        await _setup_db()
        token = _login_token("2", "acme", "instructor")
        async with create_test_client(app) as client:
            resp = await client.post(
                "/api/courses",
                json={"title": "New Course"},
                headers=_auth_header(token),
            )
            assert resp.status_code == 201
            assert resp.json()["tenant_id"] == "acme"

    async def test_admin_can_list_users(self):
        """Only admins can access GET /api/admin/users."""
        await _setup_db()
        token = _login_token("1", "acme", "admin")
        async with create_test_client(app) as client:
            resp = await client.get("/api/admin/users", headers=_auth_header(token))
            assert resp.status_code == 200
            users = resp.json()
            # Only acme users (3), not globex
            assert len(users) == 3
            assert all(u["tenant_id"] == "acme" for u in users)


class TestMultitenant:
    async def test_tenant_isolation(self):
        """Acme user only sees Acme courses, not Globex courses.

        Validates that TenantContext + manual filtering isolates data
        between tenants even without PostgreSQL RLS.
        """
        await _setup_db()
        acme_token = _login_token("1", "acme", "admin")
        globex_token = _login_token("4", "globex", "admin")
        async with create_test_client(app) as client:
            # Acme sees only Acme course
            resp = await client.get("/api/courses", headers=_auth_header(acme_token))
            assert resp.status_code == 200
            acme_courses = resp.json()
            assert len(acme_courses) == 1
            assert acme_courses[0]["title"] == "Acme Python 101"

            # Globex sees only Globex course
            resp = await client.get("/api/courses", headers=_auth_header(globex_token))
            assert resp.status_code == 200
            globex_courses = resp.json()
            assert len(globex_courses) == 1
            assert globex_courses[0]["title"] == "Globex Data Science"
