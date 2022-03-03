from sqlalchemy import Column, Integer

from AlbertoX3.database import Base, db, db_wrapper


class ItemModel(Base):
    __tablename__ = "item"

    id: Column | int = Column(
        Integer, primary_key=True, unique=True, autoincrement=False, nullable=False
    )
    max_available: Column | int | None = Column(Integer, nullable=True)

    @staticmethod
    @db_wrapper
    async def add(
        id: int,  # noqa
        max_available: int | None = None,
    ) -> "ItemModel":
        return await db.add(
            ItemModel(
                id=id,
                max_available=max_available,
            )
        )

    @staticmethod
    @db_wrapper
    async def get(
        id: int,  # noqa
    ) -> "ItemModel":
        return await db.get(ItemModel, id=id)
