from sqlalchemy import Column, Integer, BigInteger

from AlbertoX3.database import Base, db, db_wrapper, filter_by


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


class InventoryModel(Base):
    __tablename__ = "inventory"

    id: Column | int = Column(
        Integer, primary_key=True, unique=True, autoincrement=True, nullable=False
    )
    user: Column | int = Column(BigInteger, unique=False, nullable=False)
    item: Column | int = Column(Integer, nullable=False)
    quantity: Column | int = Column(Integer, nullable=False)

    @staticmethod
    @db_wrapper
    async def update(
        user: int,
        item: int,
        quantity: int,
    ) -> "InventoryModel":
        if (inv := await db.get(InventoryModel, user=user, item=item)) is None:
            return await db.add(
                InventoryModel(
                    user=user,
                    item=item,
                    quantity=quantity,
                )
            )
        inv.quantity = quantity
        return inv

    @staticmethod
    @db_wrapper
    async def get(
        user: int,
        item: int | None = None,
    ) -> "list[InventoryModel] | InventoryModel":
        if item is None:
            return await db.all(filter_by(InventoryModel, user=user))
        return await db.get(InventoryModel, user=user, item=item) or await db.add(
            InventoryModel(user=user, item=item, quantity=0)
        )
