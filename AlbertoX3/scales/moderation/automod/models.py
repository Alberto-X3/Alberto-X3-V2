from __future__ import annotations


from datetime import datetime

from sqlalchemy import Column, Integer, Text

from AlbertoX3.database import Base, UTCDatetime, db


class BadWordsModel(Base):
    __tablename__ = "bad_words"

    id: Column | int = Column(
        Integer, primary_key=True, unique=True, autoincrement=True, nullable=False
    )
    word: Column | str = Column(Text, nullable=False, unique=True)
    weight: Column | int = Column(Integer, nullable=False)
    reason: Column | str = Column(Text, nullable=False)
    timestamp: Column | datetime = Column(UTCDatetime, nullable=False)

    @staticmethod
    async def add(word: str, weight: int, reason: str) -> BadWordsModel:
        return await db.add(
            BadWordsModel(
                word=word,
                weight=weight,
                reason=reason,
                timestamp=datetime.utcnow(),
            )
        )


class ScamLinksModel(Base):
    __tablename__ = "scam_links"

    id: Column | int = Column(
        Integer, primary_key=True, unique=True, autoincrement=True, nullable=False
    )
    link: Column | str = Column(Text, nullable=False, unique=True)
    reason: Column | str = Column(Text, nullable=False)
    timestamp: Column | datetime = Column(UTCDatetime, nullable=False)

    @staticmethod
    async def add(link: str, reason: str) -> ScamLinksModel:
        return await db.add(
            ScamLinksModel(
                link=link,
                reason=reason,
                timestamp=datetime.utcnow(),
            )
        )
