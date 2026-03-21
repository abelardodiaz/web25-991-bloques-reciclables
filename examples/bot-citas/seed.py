"""Seed availability data: Mon-Fri 9:00-13:00 and 14:00-18:00.

Idempotent: skips if availabilities already exist.
"""

from __future__ import annotations

from datetime import time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from models import Availability


async def seed_data(session_factory: async_sessionmaker) -> None:
    """Insert default availability windows if the database is empty."""
    async with session_factory() as session:
        result = await session.execute(select(Availability).limit(1))
        if result.scalar_one_or_none() is not None:
            return  # Already seeded

        availabilities = []
        for day_of_week in range(5):  # 0=Monday through 4=Friday
            # Morning block: 9:00 - 13:00
            availabilities.append(
                Availability(
                    day_of_week=day_of_week,
                    start_time=time(9, 0),
                    end_time=time(13, 0),
                    is_active=True,
                )
            )
            # Afternoon block: 14:00 - 18:00
            availabilities.append(
                Availability(
                    day_of_week=day_of_week,
                    start_time=time(14, 0),
                    end_time=time(18, 0),
                    is_active=True,
                )
            )

        session.add_all(availabilities)
        await session.commit()
