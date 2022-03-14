from __future__ import annotations


from sqlalchemy import Column, Integer, BigInteger, Text, Boolean
from typing import TYPE_CHECKING

from AlbertoX3.database import Base, db, filter_by


if TYPE_CHECKING:
    from typing import List


async def get_group(group: str) -> List[YesNoModel, QuadChoiceModel]:
    return await db.all(filter_by(YesNoModel, group=group)) + await db.all(
        filter_by(QuadChoiceModel, group=group)
    )


class YesNoModel(Base):
    __tablename__ = "quiz_yesno"

    id: Column | int = Column(
        Integer, primary_key=True, unique=True, autoincrement=True, nullable=False
    )
    group: Column | str = Column(Text(64), nullable=False)
    creator: Column | int = Column(BigInteger, nullable=False)
    question: Column | str = Column(Text(128), nullable=False)
    is_true: Column | bool = Column(Boolean, nullable=False)


class QuadChoiceModel(Base):
    __tablename__ = "quiz_quad"

    id: Column | int = Column(
        Integer, primary_key=True, unique=True, autoincrement=True, nullable=False
    )
    group: Column | str = Column(Text(64), nullable=False)
    creator: Column | int = Column(BigInteger, nullable=False)
    question: Column | str = Column(Text(128), nullable=False)
    correct: Column | str = Column(Text(64), nullable=False)
    false1: Column | str = Column(Text(64), nullable=False)
    false2: Column | str = Column(Text(64), nullable=False)
    false3: Column | str = Column(Text(64), nullable=False)
