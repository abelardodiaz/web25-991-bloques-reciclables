"""EduSync models using ulfblk-db and ulfblk-scheduling mixins."""

from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, String, Text, Float

from ulfblk_db import Base, TimestampMixin
from ulfblk_scheduling import AppointmentMixin, AvailabilityMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False, default="student")
    tenant_id = Column(String(100), nullable=False, default="default")


class Course(Base, TimestampMixin):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    instructor_id = Column(String(100), nullable=False, default="")
    tenant_id = Column(String(100), nullable=False, default="default")
    status = Column(String(20), default="published")


class Lesson(Base):
    __tablename__ = "lessons"
    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    order = Column(Integer, nullable=False, default=1)
    duration_minutes = Column(Integer, default=30)


class Enrollment(Base, TimestampMixin):
    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    student_id = Column(String(100), nullable=False)
    status = Column(String(20), default="active")


class Progress(Base):
    __tablename__ = "progress"
    id = Column(Integer, primary_key=True, autoincrement=True)
    enrollment_id = Column(Integer, ForeignKey("enrollments.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    status = Column(String(20), default="not_started")
    score = Column(Float, nullable=True)


class LiveSession(Base, AppointmentMixin, TimestampMixin):
    __tablename__ = "live_sessions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    instructor_id = Column(String(100), nullable=False)
    meet_url = Column(String(500), nullable=True)


class InstructorAvailability(Base, AvailabilityMixin):
    __tablename__ = "instructor_availability"
    id = Column(Integer, primary_key=True, autoincrement=True)
