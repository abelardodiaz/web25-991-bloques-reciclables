"""Seed data: users, courses, lessons, and instructor availability."""

from __future__ import annotations

from datetime import time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from models import User, Course, Lesson, InstructorAvailability


async def seed_data(session_factory: async_sessionmaker) -> None:
    async with session_factory() as session:
        result = await session.execute(select(User).limit(1))
        if result.scalar_one_or_none() is not None:
            return  # Already seeded

        # Users - Tenant: acme
        session.add(User(username="admin-a", role="admin", tenant_id="acme"))
        session.add(User(username="teacher-a", role="instructor", tenant_id="acme"))
        session.add(User(username="student-a", role="student", tenant_id="acme"))
        # Users - Tenant: globex
        session.add(User(username="admin-b", role="admin", tenant_id="globex"))
        session.add(User(username="student-b", role="student", tenant_id="globex"))
        await session.flush()

        # Courses
        c1 = Course(
            title="Python Fundamentals",
            description="Learn Python from zero to hero",
            instructor_id="2", tenant_id="acme",
        )
        c2 = Course(
            title="FastAPI Mastery",
            description="Build production APIs with FastAPI",
            instructor_id="2", tenant_id="acme",
        )
        c3 = Course(
            title="Data Science Intro",
            description="Introduction to data science",
            instructor_id="4", tenant_id="globex",
        )
        session.add_all([c1, c2, c3])
        await session.flush()

        # Lessons for Python Fundamentals
        for i, title in enumerate([
            "Variables and Types",
            "Control Flow",
            "Functions",
            "Classes and Objects",
        ], start=1):
            session.add(Lesson(
                course_id=c1.id, title=title,
                content=f"Content for {title}", order=i, duration_minutes=45,
            ))

        # Lessons for FastAPI Mastery
        for i, title in enumerate([
            "Hello World API",
            "Path Parameters",
            "Request Bodies",
        ], start=1):
            session.add(Lesson(
                course_id=c2.id, title=title,
                content=f"Content for {title}", order=i, duration_minutes=30,
            ))

        # Instructor availability Mon-Fri 9-13, 14-18
        for dow in range(5):
            session.add(InstructorAvailability(
                day_of_week=dow, start_time=time(9, 0), end_time=time(13, 0),
                is_active=True, resource_id="2",
            ))
            session.add(InstructorAvailability(
                day_of_week=dow, start_time=time(14, 0), end_time=time(18, 0),
                is_active=True, resource_id="2",
            ))

        await session.commit()
