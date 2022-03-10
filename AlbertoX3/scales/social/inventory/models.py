from sqlalchemy import Column, Integer, BigInteger, Boolean

from AlbertoX3.database import Base, db, filter_by


class ItemModel(Base):
    __tablename__ = "item"

    id: Column | int = Column(
        Integer, primary_key=True, unique=True, autoincrement=False, nullable=False
    )
    buyable: Column | bool = Column(Boolean, nullable=False)
    price: Column | int = Column(Integer, nullable=True)
    max_available: Column | int | None = Column(Integer, nullable=True)

    @staticmethod
    async def add(
        id: int,  # noqa
        buyable: bool = False,
        price: int | None = None,
        max_available: int | None = None,
    ) -> "ItemModel":
        return await db.add(
            ItemModel(
                id=id,
                buyable=buyable,
                price=price,
                max_available=max_available,
            )
        )

    @staticmethod
    async def get(
        id: int,  # noqa
    ) -> "ItemModel | None":
        return await db.get(ItemModel, id=id)

    async def get_claimed_amount(self) -> int:
        return sum(
            map(
                lambda i: i.quantity,
                await db.all(filter_by(InventoryModel, item=self.id)),
            )
        )


class InventoryModel(Base):
    __tablename__ = "inventory"

    id: Column | int = Column(
        Integer, primary_key=True, unique=True, autoincrement=True, nullable=False
    )
    user: Column | int = Column(BigInteger, unique=False, nullable=False)
    item: Column | int = Column(Integer, nullable=False)
    quantity: Column | int = Column(Integer, nullable=False)

    @staticmethod
    async def update(
        user: int,
        item: int,
        quantity: int,
        relative: bool = False,
    ) -> "InventoryModel":
        inv = await InventoryModel.get(user, item)
        if relative:
            quantity = inv.quantity + quantity
        inv.quantity = quantity
        return inv

    @staticmethod
    async def get(
        user: int,
        item: int | None = None,
    ) -> "list[InventoryModel] | InventoryModel":
        if item is None:
            return await db.all(filter_by(InventoryModel, user=user))
        return await db.get(InventoryModel, user=user, item=item) or await db.add(
            InventoryModel(user=user, item=item, quantity=0)
        )
