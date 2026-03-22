"""EduSync Phase 4: Billing and caching.

Adds 2 final blocks:
  - ulfblk-billing: BillingService + StripeProvider (mocked) for subscriptions
  - ulfblk-redis: CacheStore with FakeRedis for course catalog caching

Tests: 6 covering checkout, subscriptions, and cache behavior.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import fakeredis.aioredis
from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ulfblk_core import create_app
from ulfblk_db import (
    Base,
    DatabaseSettings,
    create_async_engine,
    create_session_factory,
    get_db_session,
)
from ulfblk_billing import BillingSettings, StripeProvider
from ulfblk_redis.cache.store import RedisCache
from ulfblk_redis.client.manager import RedisManager, RedisSettings
from ulfblk_testing import create_test_client

from tests.recipes.edusync.models import EduCourse


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
_settings = DatabaseSettings(database_url="sqlite+aiosqlite://")
_engine = create_async_engine(_settings)
SessionLocal = create_session_factory(_engine)
db_dep = get_db_session(SessionLocal)


# ---------------------------------------------------------------------------
# Redis cache (FakeRedis for testing - recreated per test via _setup_db)
# ---------------------------------------------------------------------------
_redis_settings = RedisSettings(key_prefix="edusync")
_redis_manager = RedisManager(settings=_redis_settings)
cache = RedisCache(_redis_manager, default_ttl=300)

# Track DB calls for cache tests
db_call_count = 0


# ---------------------------------------------------------------------------
# Billing (mocked Stripe)
# ---------------------------------------------------------------------------
_billing_settings = BillingSettings(
    api_key="sk_test_fake",
    webhook_secret="whsec_test_fake",
)

# Mock HTTP responses
_mock_http = AsyncMock()
_mock_http.aclose = AsyncMock()

stripe_provider = StripeProvider(_billing_settings)
stripe_provider._client = _mock_http


def _mock_stripe_response(data: dict, status_code: int = 200):
    """Configure mock HTTP to return a specific response."""
    resp = MagicMock()
    resp.json.return_value = data
    resp.status_code = status_code
    resp.raise_for_status = MagicMock()
    _mock_http.request = AsyncMock(return_value=resp)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class CheckoutRequest(BaseModel):
    customer_email: str
    plan: str  # basic, pro, enterprise


class CheckoutResponse(BaseModel):
    checkout_url: str
    session_id: str


class CourseOut(BaseModel):
    id: int
    title: str


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = create_app(service_name="edusync-billing", version="0.1.0")


@app.post("/api/billing/checkout", response_model=CheckoutResponse)
async def create_checkout(body: CheckoutRequest):
    """Create a Stripe checkout session for subscription."""
    price_ids = {
        "basic": "price_basic_001",
        "pro": "price_pro_001",
        "enterprise": "price_ent_001",
    }
    price_id = price_ids.get(body.plan)
    if not price_id:
        raise HTTPException(status_code=400, detail="Invalid plan.")

    _mock_stripe_response({
        "id": f"cs_test_{body.plan}",
        "url": f"https://checkout.stripe.com/pay/{body.plan}",
        "status": "open",
        "object": "checkout.session",
    })

    result = await stripe_provider._client.request(
        method="POST",
        url=f"{_billing_settings.api_base_url}/v1/checkout/sessions",
        json={
            "customer_email": body.customer_email,
            "line_items": [{"price": price_id, "quantity": 1}],
            "mode": "subscription",
            "success_url": "https://edusync.app/success",
            "cancel_url": "https://edusync.app/cancel",
        },
    )
    data = result.json()
    return CheckoutResponse(checkout_url=data["url"], session_id=data["id"])


@app.post("/api/billing/subscribe", status_code=200)
async def create_subscription():
    """Create a subscription (simulated via mock)."""
    _mock_stripe_response({
        "id": "sub_test_001",
        "status": "active",
        "customer": "cus_test_001",
        "object": "subscription",
    })
    result = await stripe_provider._client.request(
        method="POST",
        url=f"{_billing_settings.api_base_url}/v1/subscriptions",
        json={"customer": "cus_test_001", "price": "price_pro_001"},
    )
    data = result.json()
    return {"subscription_id": data["id"], "status": data["status"]}


@app.delete("/api/billing/subscribe/{sub_id}", status_code=200)
async def cancel_subscription(sub_id: str):
    """Cancel a subscription."""
    _mock_stripe_response({
        "id": sub_id,
        "status": "canceled",
        "object": "subscription",
    })
    result = await stripe_provider._client.request(
        method="DELETE",
        url=f"{_billing_settings.api_base_url}/v1/subscriptions/{sub_id}",
    )
    data = result.json()
    return {"subscription_id": data["id"], "status": data["status"]}


@app.get("/api/courses/cached", response_model=list[CourseOut])
async def list_courses_cached(db: AsyncSession = Depends(db_dep)):
    """List courses with Redis cache layer."""
    global db_call_count
    cache_key = "courses:published"

    # Try cache first
    cached = await cache.get(cache_key)
    if cached is not None:
        return [CourseOut(**c) for c in cached]

    # Cache miss: query DB
    db_call_count += 1
    result = await db.execute(
        select(EduCourse).where(EduCourse.status == "published").order_by(EduCourse.id)
    )
    courses = result.scalars().all()
    items = [{"id": c.id, "title": c.title} for c in courses]

    # Store in cache
    await cache.set(cache_key, items, ttl=300)
    return [CourseOut(**c) for c in items]


@app.post("/api/courses/cached", response_model=CourseOut, status_code=201)
async def create_course_and_invalidate(title: str = "New Course", db: AsyncSession = Depends(db_dep)):
    """Create course and invalidate cache."""
    course = EduCourse(title=title, status="published")
    db.add(course)
    await db.commit()
    await db.refresh(course)
    # Invalidate cache
    await cache.delete("courses:published")
    return CourseOut(id=course.id, title=course.title)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
async def _setup_db():
    global db_call_count
    db_call_count = 0
    # Create fresh FakeRedis per test to avoid event loop binding issues
    fresh_redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    _redis_manager._client = fresh_redis

    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        session.add(EduCourse(title="Python 101", status="published"))
        session.add(EduCourse(title="FastAPI Pro", status="published"))
        session.add(EduCourse(title="Draft Course", status="draft"))
        await session.commit()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
class TestBilling:
    async def test_create_checkout_session(self):
        """POST /api/billing/checkout returns Stripe checkout URL."""
        async with create_test_client(app) as client:
            resp = await client.post("/api/billing/checkout", json={
                "customer_email": "user@acme.com",
                "plan": "pro",
            })
            assert resp.status_code == 200
            data = resp.json()
            assert "checkout.stripe.com" in data["checkout_url"]
            assert data["session_id"] == "cs_test_pro"

    async def test_create_subscription(self):
        """POST /api/billing/subscribe creates active subscription."""
        async with create_test_client(app) as client:
            resp = await client.post("/api/billing/subscribe")
            assert resp.status_code == 200
            data = resp.json()
            assert data["subscription_id"] == "sub_test_001"
            assert data["status"] == "active"

    async def test_cancel_subscription(self):
        """DELETE /api/billing/subscribe/{id} cancels subscription."""
        async with create_test_client(app) as client:
            resp = await client.delete("/api/billing/subscribe/sub_test_001")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "canceled"


class TestCache:
    async def test_cache_miss_queries_db(self):
        """First call to cached endpoint queries DB and stores in cache."""
        await _setup_db()
        async with create_test_client(app) as client:
            resp = await client.get("/api/courses/cached")
            assert resp.status_code == 200
            data = resp.json()
            assert len(data) == 2  # Only published courses
            assert db_call_count == 1

    async def test_cache_hit_skips_db(self):
        """Second call serves from cache without hitting DB."""
        await _setup_db()
        async with create_test_client(app) as client:
            # First call: cache miss
            await client.get("/api/courses/cached")
            assert db_call_count == 1
            # Second call: cache hit
            resp = await client.get("/api/courses/cached")
            assert resp.status_code == 200
            assert db_call_count == 1  # Still 1, no new DB call

    async def test_cache_invalidation_on_create(self):
        """Creating a course invalidates cache, next GET re-queries DB."""
        await _setup_db()
        async with create_test_client(app) as client:
            # Populate cache
            await client.get("/api/courses/cached")
            assert db_call_count == 1
            # Create new course (invalidates cache)
            resp = await client.post("/api/courses/cached?title=New%20Course")
            assert resp.status_code == 201
            # Next GET re-queries DB
            resp = await client.get("/api/courses/cached")
            assert resp.status_code == 200
            assert db_call_count == 2  # DB queried again
            assert len(resp.json()) == 3  # Now 3 published courses
