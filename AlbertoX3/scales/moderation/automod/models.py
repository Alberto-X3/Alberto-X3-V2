from __future__ import annotations


from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, Text

from AlbertoX3.database import Base, UTCDatetime, db, db_wrapper

if TYPE_CHECKING:
    from typing import Optional


class BadWordsModel(Base):
    __tablename__ = "bad_words"

    id: Column | int = Column(
        Integer, primary_key=True, unique=True, autoincrement=True, nullable=False
    )
    word: Column | str = Column(Text, nullable=False)
    weight: Column | int = Column(Integer, nullable=False)
    reason: Column | Optional[str] = Column(Text)
    timestamp: Column | datetime = Column(UTCDatetime, nullable=False)
    occurrence: Column | int = Column(Integer, nullable=False, default=0)

    @staticmethod
    async def add(word: str, weight: int, reason: str = None) -> BadWordsModel:
        return await db.add(
            BadWordsModel(
                word=word,
                weight=weight,
                reason=reason,
                timestamp=datetime.utcnow(),
            )
        )

    @staticmethod
    async def update(word: str, weight: int, reason: str = None) -> BadWordsModel:
        if old := await db.get(BadWordsModel, word=word):
            old.weight = weight
            if reason:
                old.reason = reason
            return old
        else:
            return await BadWordsModel.add(word, weight, reason)

    @staticmethod
    @db_wrapper
    async def sync_from_csv(path: Path | str):
        # structure of csv: WORD,WEIGHT,optional(REASON)
        # first line of csv will be ignored
        first = True
        with open(path, encoding="utf-8") as f:
            for line in f.readlines():
                if first:
                    first = False
                    continue
                word, weight, *reason = line.removesuffix("\n").split(",")
                await BadWordsModel.update(word, int(weight), ",".join(reason) or None)


class ScamLinksModel(Base):
    __tablename__ = "scam_links"

    id: Column | int = Column(
        Integer, primary_key=True, unique=True, autoincrement=True, nullable=False
    )
    link: Column | str = Column(Text, nullable=False)
    reason: Column | Optional[str] = Column(Text)
    timestamp: Column | datetime = Column(UTCDatetime, nullable=False)
    occurrence: Column | int = Column(Integer, nullable=False, default=0)

    @staticmethod
    async def add(link: str, reason: str = None) -> ScamLinksModel:
        return await db.add(
            ScamLinksModel(
                link=link,
                reason=reason,
                timestamp=datetime.utcnow(),
            )
        )

    @staticmethod
    async def update(link: str, reason: str = None) -> ScamLinksModel:
        if old := await db.get(ScamLinksModel, link=link):
            if reason:
                old.reason = reason
            return old
        else:
            return await ScamLinksModel.add(link, reason)

    @staticmethod
    @db_wrapper
    async def sync_from_csv(path: Path | str):
        # structure of csv: LINK,optional(REASON)
        # first line of csv will be ignored
        first = True
        with open(path, encoding="utf-8") as f:
            for line in f.readlines():
                if first:
                    first = False
                    continue
                link, *reason = line.removesuffix("\n").split(",")
                await ScamLinksModel.update(link, ",".join(reason) or None)
