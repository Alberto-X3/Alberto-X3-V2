from __future__ import annotations


from datetime import datetime, timezone

from sqlalchemy import Column, BigInteger

from AlbertoX3.database import Base, UTCDatetime, db


class ActivityModel(Base):
    __tablename__ = "activity"

    member: Column | int = Column(
        BigInteger, primary_key=True, unique=True, nullable=False
    )
    timestamp: Column | datetime = Column(UTCDatetime, nullable=False)

    @staticmethod
    async def add(member: int, timestamp: datetime | int = None) -> ActivityModel:
        if isinstance(timestamp, int):
            timestamp = datetime.fromtimestamp(timestamp)
        return await db.add(
            ActivityModel(
                member=member,
                timestamp=timestamp or datetime.utcnow(),
            )
        )

    @staticmethod
    async def update(
        member: int, timestamp: datetime | float | int = None
    ) -> ActivityModel:
        if isinstance(timestamp, (float, int)):
            try:
                timestamp = datetime.fromtimestamp(timestamp)
            except ValueError:
                timestamp = datetime.fromtimestamp(timestamp / 1000)
        if timestamp is None:
            timestamp = datetime.utcnow()
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        if not (row := await db.get(ActivityModel, member=member)):
            row = await ActivityModel.add(member, timestamp)
        elif timestamp > row.timestamp:
            row.timestamp = timestamp
        return row
