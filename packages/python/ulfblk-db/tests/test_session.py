"""Tests for session factory and dependency."""

import inspect

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ulfblk_db import create_session_factory, get_db_session


class TestCreateSessionFactory:
    def test_returns_sessionmaker(self, async_engine):
        factory = create_session_factory(async_engine)
        assert isinstance(factory, async_sessionmaker)

    async def test_produces_async_session(self, session_factory):
        async with session_factory() as session:
            assert isinstance(session, AsyncSession)

    def test_expire_on_commit_false(self, session_factory):
        assert session_factory.kw.get("expire_on_commit") is False


class TestGetDbSession:
    def test_returns_callable(self, session_factory):
        dep = get_db_session(session_factory)
        assert callable(dep)

    async def test_yields_and_closes_session(self, session_factory):
        dep = get_db_session(session_factory)
        gen = dep()
        session = await gen.__anext__()
        assert isinstance(session, AsyncSession)
        try:
            await gen.__anext__()
        except StopAsyncIteration:
            pass
