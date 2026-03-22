"""Shared EduSync models used across all test phases.

Superset of all columns needed by phases 1-4. Class names and table names
prefixed with 'Edu'/'edu_' to avoid SQLAlchemy registry and metadata
conflicts with other test suites.
"""

from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, String, Text, Float

from ulfblk_db import Base, TimestampMixin
from ulfblk_scheduling import AppointmentMixin, AvailabilityMixin


class EduUser(Base, TimestampMixin):
    __tablename__ = "edu_users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False, default="student")
    tenant_id = Column(String(100), nullable=False, default="default")


class EduCourse(Base, TimestampMixin):
    __tablename__ = "edu_courses"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    content_summary = Column(Text, nullable=True)
    instructor_id = Column(String(100), nullable=False, default="")
    tenant_id = Column(String(100), nullable=False, default="default")
    status = Column(String(20), default="published")


class EduLesson(Base):
    __tablename__ = "edu_lessons"
    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("edu_courses.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    order = Column(Integer, nullable=False, default=1)
    duration_minutes = Column(Integer, default=30)


class EduEnrollment(Base, TimestampMixin):
    __tablename__ = "edu_enrollments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("edu_courses.id"), nullable=False)
    student_id = Column(String(100), nullable=False)
    status = Column(String(20), default="active")


class EduProgress(Base):
    __tablename__ = "edu_progress"
    id = Column(Integer, primary_key=True, autoincrement=True)
    enrollment_id = Column(Integer, ForeignKey("edu_enrollments.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("edu_lessons.id"), nullable=False)
    status = Column(String(20), default="not_started")
    score = Column(Float, nullable=True)


class EduLiveSession(Base, AppointmentMixin, TimestampMixin):
    """Reuses AppointmentMixin for instructor live sessions."""
    __tablename__ = "edu_live_sessions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("edu_courses.id"), nullable=False)
    instructor_id = Column(String(100), nullable=False)
    meet_url = Column(String(500), nullable=True)


class EduInstructorAvailability(Base, AvailabilityMixin):
    """Reuses AvailabilityMixin for instructor schedules."""
    __tablename__ = "edu_instructor_availability"
    id = Column(Integer, primary_key=True, autoincrement=True)
