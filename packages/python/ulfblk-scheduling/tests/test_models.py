"""Tests for scheduling model mixins."""

from __future__ import annotations

from datetime import datetime, time, timezone

from sqlalchemy import Column, Integer, inspect as sa_inspect
from sqlalchemy.orm import DeclarativeBase

from ulfblk_scheduling import AppointmentMixin, AvailabilityMixin, BlockedSlotMixin


class _Base(DeclarativeBase):
    pass


class TestAppointmentMixin:
    def test_has_appointment_columns(self):
        class _ApptModel(_Base, AppointmentMixin):
            __tablename__ = "_test_appt"
            id = Column(Integer, primary_key=True)

        mapper = sa_inspect(_ApptModel)
        column_names = [c.key for c in mapper.columns]
        assert "scheduled_at" in column_names
        assert "duration_minutes" in column_names
        assert "status" in column_names
        assert "resource_id" in column_names
        assert "notes" in column_names

    def test_scheduled_at_has_timezone(self):
        class _ApptModel2(_Base, AppointmentMixin):
            __tablename__ = "_test_appt2"
            id = Column(Integer, primary_key=True)

        mapper = sa_inspect(_ApptModel2)
        col = mapper.columns["scheduled_at"]
        assert col.type.timezone is True

    def test_default_status_column(self):
        class _ApptModel3(_Base, AppointmentMixin):
            __tablename__ = "_test_appt3"
            id = Column(Integer, primary_key=True)

        mapper = sa_inspect(_ApptModel3)
        status_col = mapper.columns["status"]
        assert status_col.default.arg == "pending"

    def test_default_duration_column(self):
        class _ApptModel3b(_Base, AppointmentMixin):
            __tablename__ = "_test_appt3b"
            id = Column(Integer, primary_key=True)

        mapper = sa_inspect(_ApptModel3b)
        duration_col = mapper.columns["duration_minutes"]
        assert duration_col.default.arg == 30

    def test_cancel(self):
        class _ApptModel4(_Base, AppointmentMixin):
            __tablename__ = "_test_appt4"
            id = Column(Integer, primary_key=True)

        obj = _ApptModel4(scheduled_at=datetime.now(timezone.utc))
        obj.cancel()
        assert obj.status == "cancelled"

    def test_confirm(self):
        class _ApptModel5(_Base, AppointmentMixin):
            __tablename__ = "_test_appt5"
            id = Column(Integer, primary_key=True)

        obj = _ApptModel5(scheduled_at=datetime.now(timezone.utc))
        obj.confirm()
        assert obj.status == "confirmed"

    def test_complete(self):
        class _ApptModel6(_Base, AppointmentMixin):
            __tablename__ = "_test_appt6"
            id = Column(Integer, primary_key=True)

        obj = _ApptModel6(scheduled_at=datetime.now(timezone.utc))
        obj.complete()
        assert obj.status == "completed"

    def test_mark_no_show(self):
        class _ApptModel7(_Base, AppointmentMixin):
            __tablename__ = "_test_appt7"
            id = Column(Integer, primary_key=True)

        obj = _ApptModel7(scheduled_at=datetime.now(timezone.utc))
        obj.mark_no_show()
        assert obj.status == "no_show"


class TestAvailabilityMixin:
    def test_has_availability_columns(self):
        class _AvailModel(_Base, AvailabilityMixin):
            __tablename__ = "_test_avail"
            id = Column(Integer, primary_key=True)

        mapper = sa_inspect(_AvailModel)
        column_names = [c.key for c in mapper.columns]
        assert "day_of_week" in column_names
        assert "start_time" in column_names
        assert "end_time" in column_names
        assert "resource_id" in column_names
        assert "is_active" in column_names

    def test_default_is_active_column(self):
        class _AvailModel2(_Base, AvailabilityMixin):
            __tablename__ = "_test_avail2"
            id = Column(Integer, primary_key=True)

        mapper = sa_inspect(_AvailModel2)
        is_active_col = mapper.columns["is_active"]
        assert is_active_col.default.arg is True


class TestBlockedSlotMixin:
    def test_has_blocked_slot_columns(self):
        class _BlockModel(_Base, BlockedSlotMixin):
            __tablename__ = "_test_block"
            id = Column(Integer, primary_key=True)

        mapper = sa_inspect(_BlockModel)
        column_names = [c.key for c in mapper.columns]
        assert "start_at" in column_names
        assert "end_at" in column_names
        assert "resource_id" in column_names
        assert "reason" in column_names

    def test_start_at_has_timezone(self):
        class _BlockModel2(_Base, BlockedSlotMixin):
            __tablename__ = "_test_block2"
            id = Column(Integer, primary_key=True)

        mapper = sa_inspect(_BlockModel2)
        start_col = mapper.columns["start_at"]
        end_col = mapper.columns["end_at"]
        assert start_col.type.timezone is True
        assert end_col.type.timezone is True

    def test_nullable_fields(self):
        class _BlockModel3(_Base, BlockedSlotMixin):
            __tablename__ = "_test_block3"
            id = Column(Integer, primary_key=True)

        obj = _BlockModel3(
            start_at=datetime.now(timezone.utc),
            end_at=datetime.now(timezone.utc),
        )
        assert obj.resource_id is None
        assert obj.reason is None
