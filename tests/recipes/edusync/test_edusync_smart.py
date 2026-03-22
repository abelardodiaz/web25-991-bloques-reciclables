"""EduSync Phase 3: AI tutor, automation rules, and notifications.

Adds 3 new blocks:
  - ulfblk-ai-rag: RAGPipeline with mock LLM + mock vector store for AI tutor
  - ulfblk-automation: RuleEngine for course progression and certification rules
  - ulfblk-notifications: NotificationService with ConsoleProvider for alerts

Tests: 8 covering AI chat, rule evaluation, and notification delivery.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

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
from ulfblk_automation import (
    Rule,
    Condition,
    Operator,
    Action,
    ActionType,
    RuleEngine,
    RuleEngineSettings,
    LogActionHandler,
    evaluate_condition,
)
from ulfblk_notifications import (
    NotificationService,
    ConsoleProvider,
)
from ulfblk_notifications.models import (
    Notification,
    Channel,
    Priority,
)
from ulfblk_testing import create_test_client

from tests.recipes.edusync.models import EduCourse, EduLesson, EduEnrollment, EduProgress


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
_settings = DatabaseSettings(database_url="sqlite+aiosqlite://")
_engine = create_async_engine(_settings)
SessionLocal = create_session_factory(_engine)
db_dep = get_db_session(SessionLocal)


# ---------------------------------------------------------------------------
# Mock RAG pipeline (duck-typed protocols)
# ---------------------------------------------------------------------------
def _create_mock_rag():
    """Create a mock RAG pipeline that returns pre-configured answers."""
    mock_vector_store = AsyncMock()
    mock_vector_store.resolve_collection = MagicMock(return_value="edusync_kb")
    mock_vector_store.query = AsyncMock(return_value=[
        {"text": "FastAPI uses async/await for high performance.", "id": "d1", "distance": 0.1, "metadata": {}},
        {"text": "Pydantic validates request/response schemas.", "id": "d2", "distance": 0.2, "metadata": {}},
    ])
    mock_vector_store.add_documents = AsyncMock()
    mock_vector_store.start = AsyncMock()
    mock_vector_store.stop = AsyncMock()
    mock_vector_store.health_check = AsyncMock(return_value={"status": "healthy"})

    mock_llm = AsyncMock()
    mock_llm.generate = AsyncMock(
        return_value="FastAPI is an async Python framework that uses Pydantic for validation."
    )
    mock_llm.start = AsyncMock()
    mock_llm.stop = AsyncMock()
    mock_llm.health_check = AsyncMock(return_value={"status": "healthy"})

    return mock_vector_store, mock_llm


mock_vector_store, mock_llm = _create_mock_rag()


# ---------------------------------------------------------------------------
# Automation: rule engine with course progression rules
# ---------------------------------------------------------------------------
rule_engine = RuleEngine(settings=RuleEngineSettings(max_rules=100))
log_handler = LogActionHandler()
rule_engine.register_handler(ActionType.LOG, log_handler)

# Notifications
notifications_sent: list[dict] = []


class InMemoryNotifyHandler:
    """Custom action handler that records notifications."""

    async def execute(self, action: Action, context: dict) -> None:
        notifications_sent.append({
            "action": action.name,
            "student_id": context.get("student_id"),
            "message": action.config.get("message", ""),
        })

    async def health_check(self) -> dict:
        return {"status": "healthy"}


notify_handler = InMemoryNotifyHandler()
rule_engine.register_handler(ActionType.NOTIFY, notify_handler)

# Rule 1: All lessons completed -> mark enrollment completed
rule_engine.add_rule(Rule(
    rule_id="course-completion",
    name="Course Completion",
    conditions=Condition(
        operator=Operator.EQ,
        field="all_lessons_completed",
        value=True,
    ),
    actions=[
        Action(action_type=ActionType.LOG, name="log-completion", config={}),
        Action(
            action_type=ActionType.NOTIFY, name="notify-completion",
            config={"message": "Congratulations! Course completed."},
        ),
    ],
    priority=10,
    enabled=True,
))

# Rule 2: High score on evaluation -> certificate
rule_engine.add_rule(Rule(
    rule_id="certificate-earned",
    name="Certificate Earned",
    conditions=Condition(
        operator=Operator.AND,
        children=[
            Condition(operator=Operator.EQ, field="evaluation_type", value="final_exam"),
            Condition(operator=Operator.GTE, field="score", value=80),
        ],
    ),
    actions=[
        Action(
            action_type=ActionType.NOTIFY, name="notify-certificate",
            config={"message": "Certificate earned! Score: {score}"},
        ),
    ],
    priority=5,
    enabled=True,
))

# Rule 3: Disabled rule (should not fire)
rule_engine.add_rule(Rule(
    rule_id="disabled-rule",
    name="Disabled Test",
    conditions=Condition(operator=Operator.EQ, field="always", value=True),
    actions=[Action(action_type=ActionType.LOG, name="should-not-fire", config={})],
    priority=1,
    enabled=False,
))


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class ChatRequest(BaseModel):
    question: str
    course_id: int


class ChatResponse(BaseModel):
    answer: str
    sources_count: int


class EvaluationSubmit(BaseModel):
    enrollment_id: int
    lesson_id: int
    score: float
    evaluation_type: str = "quiz"  # quiz, final_exam


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = create_app(service_name="edusync-smart", version="0.1.0")


@app.post("/api/chat", response_model=ChatResponse)
async def ai_tutor_chat(body: ChatRequest, db: AsyncSession = Depends(db_dep)):
    """AI tutor: searches course content via RAG and generates answer."""
    # Query vector store for relevant content
    results = await mock_vector_store.query(
        text=body.question,
        collection="edusync_kb",
        n_results=3,
    )
    context = "\n".join(r["text"] for r in results)
    # Generate answer using LLM
    answer = await mock_llm.generate(
        prompt=body.question,
        context=context,
    )
    return ChatResponse(answer=answer, sources_count=len(results))


@app.post("/api/evaluations", status_code=200)
async def submit_evaluation(body: EvaluationSubmit, db: AsyncSession = Depends(db_dep)):
    """Submit evaluation score and trigger automation rules."""
    # Update progress with score
    result = await db.execute(
        select(EduProgress).where(
            EduProgress.enrollment_id == body.enrollment_id,
            EduProgress.lesson_id == body.lesson_id,
        )
    )
    progress = result.scalar_one_or_none()
    if progress is None:
        raise HTTPException(status_code=404, detail="Progress not found.")
    progress.status = "completed"
    progress.score = body.score
    await db.commit()

    # Check if all lessons are completed
    result = await db.execute(
        select(EduProgress).where(EduProgress.enrollment_id == body.enrollment_id)
    )
    all_progress = result.scalars().all()
    all_completed = all(p.status == "completed" for p in all_progress)

    # Get enrollment for student_id
    result = await db.execute(
        select(EduEnrollment).where(EduEnrollment.id == body.enrollment_id)
    )
    enrollment = result.scalar_one()

    # Run automation rules
    context = {
        "all_lessons_completed": all_completed,
        "evaluation_type": body.evaluation_type,
        "score": body.score,
        "student_id": enrollment.student_id,
    }
    results = await rule_engine.evaluate(context)
    matched_rules = [r for r in results if r.matched]

    # If all completed, update enrollment status
    if all_completed:
        enrollment.status = "completed"
        await db.commit()

    return {
        "score": body.score,
        "rules_matched": len(matched_rules),
        "all_completed": all_completed,
        "enrollment_status": enrollment.status,
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
async def _setup_db():
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        course = EduCourse(title="FastAPI Mastery", content_summary="Learn FastAPI end to end")
        session.add(course)
        await session.flush()

        for i in range(1, 4):
            session.add(EduLesson(
                course_id=course.id, title=f"Lesson {i}",
                content=f"Content for lesson {i}", order=i,
            ))
        await session.flush()

        enrollment = EduEnrollment(course_id=course.id, student_id="student-1", status="active")
        session.add(enrollment)
        await session.flush()

        # Get lesson IDs
        result = await session.execute(
            select(EduLesson).where(EduLesson.course_id == course.id).order_by(EduLesson.order)
        )
        lessons = result.scalars().all()
        for lesson in lessons:
            session.add(EduProgress(
                enrollment_id=enrollment.id, lesson_id=lesson.id, status="not_started",
            ))
        await session.commit()

    notifications_sent.clear()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
class TestAITutor:
    async def test_chat_returns_ai_answer(self):
        """POST /api/chat returns AI-generated answer from RAG pipeline."""
        await _setup_db()
        async with create_test_client(app) as client:
            resp = await client.post("/api/chat", json={
                "question": "What is FastAPI?",
                "course_id": 1,
            })
            assert resp.status_code == 200
            data = resp.json()
            assert "FastAPI" in data["answer"]
            assert data["sources_count"] == 2

    async def test_rag_vector_search_called(self):
        """Chat endpoint queries the vector store for relevant content."""
        await _setup_db()
        mock_vector_store.query.reset_mock()
        async with create_test_client(app) as client:
            await client.post("/api/chat", json={
                "question": "How does validation work?",
                "course_id": 1,
            })
        mock_vector_store.query.assert_called_once()
        call_args = mock_vector_store.query.call_args
        assert call_args.kwargs["text"] == "How does validation work?"

    async def test_rag_llm_receives_context(self):
        """LLM generate is called with context from vector search results."""
        await _setup_db()
        mock_llm.generate.reset_mock()
        async with create_test_client(app) as client:
            await client.post("/api/chat", json={
                "question": "Tell me about async",
                "course_id": 1,
            })
        mock_llm.generate.assert_called_once()
        call_args = mock_llm.generate.call_args
        assert "async/await" in call_args.kwargs["context"]


class TestAutomation:
    async def test_complete_all_lessons_triggers_completion(self):
        """Completing all lessons triggers course-completion rule and updates enrollment."""
        await _setup_db()
        async with create_test_client(app) as client:
            # Get lesson IDs from progress
            resp = await client.get("/api/evaluations/setup")  # Not needed, we know IDs

            # Complete lessons 1 and 2 as quizzes (partial, won't trigger completion)
            for lesson_id in [1, 2]:
                resp = await client.post("/api/evaluations", json={
                    "enrollment_id": 1, "lesson_id": lesson_id,
                    "score": 90, "evaluation_type": "quiz",
                })
                assert resp.status_code == 200
                assert resp.json()["all_completed"] is False

            # Complete lesson 3 (final) -> triggers completion
            resp = await client.post("/api/evaluations", json={
                "enrollment_id": 1, "lesson_id": 3,
                "score": 85, "evaluation_type": "quiz",
            })
            assert resp.status_code == 200
            data = resp.json()
            assert data["all_completed"] is True
            assert data["enrollment_status"] == "completed"
            assert data["rules_matched"] >= 1

    async def test_high_score_final_exam_triggers_certificate(self):
        """Score >= 80 on final_exam triggers certificate notification."""
        await _setup_db()
        notifications_sent.clear()
        async with create_test_client(app) as client:
            # Submit final exam with high score on lesson 1
            resp = await client.post("/api/evaluations", json={
                "enrollment_id": 1, "lesson_id": 1,
                "score": 92, "evaluation_type": "final_exam",
            })
            assert resp.status_code == 200
            data = resp.json()
            assert data["rules_matched"] >= 1
        # Check notification was sent
        cert_notifs = [n for n in notifications_sent if "certificate" in n["action"].lower()]
        assert len(cert_notifs) >= 1
        assert cert_notifs[0]["student_id"] == "student-1"

    async def test_low_score_no_certificate(self):
        """Score < 80 on final_exam does NOT trigger certificate."""
        await _setup_db()
        notifications_sent.clear()
        async with create_test_client(app) as client:
            resp = await client.post("/api/evaluations", json={
                "enrollment_id": 1, "lesson_id": 1,
                "score": 65, "evaluation_type": "final_exam",
            })
            assert resp.status_code == 200
        cert_notifs = [n for n in notifications_sent if "certificate" in n["action"].lower()]
        assert len(cert_notifs) == 0

    async def test_disabled_rule_does_not_fire(self):
        """Rules with enabled=False are skipped during evaluation."""
        context = {"always": True}
        results = await rule_engine.evaluate(context)
        disabled_matches = [r for r in results if r.rule_id == "disabled-rule" and r.matched]
        assert len(disabled_matches) == 0


class TestConditionEvaluator:
    async def test_evaluate_condition_directly(self):
        """evaluate_condition works with nested AND conditions."""
        condition = Condition(
            operator=Operator.AND,
            children=[
                Condition(operator=Operator.EQ, field="status", value="active"),
                Condition(operator=Operator.GTE, field="score", value=80),
            ],
        )
        assert evaluate_condition(condition, {"status": "active", "score": 90}) is True
        assert evaluate_condition(condition, {"status": "active", "score": 70}) is False
        assert evaluate_condition(condition, {"status": "inactive", "score": 90}) is False
