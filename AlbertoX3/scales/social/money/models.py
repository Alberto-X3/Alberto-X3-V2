from sqlalchemy import Column, Integer, BigInteger

from AlbertoX3.database import Base, db, db_wrapper


class MoneyModel(Base):
    __tablename__ = "money"

    id: Column | int = Column(
        Integer, primary_key=True, unique=True, autoincrement=True, nullable=False
    )
    user: Column | int = Column(BigInteger, unique=True, nullable=False)
    amount: Column | int = Column(Integer, nullable=False)

    @staticmethod
    @db_wrapper
    async def update(
        user: int,
        amount: int,
        relative: bool = False,
    ) -> "MoneyModel":
        inv = await db.get(MoneyModel, user=user) or await db.add(
            MoneyModel(user=user, amount=0)
        )
        # similar to MoneyModel.get, but this would
        # close the connection to the database
        if relative:
            amount = inv.amount + amount
        inv.amount = amount
        return inv

    @staticmethod
    @db_wrapper
    async def get(
        user: int,
    ) -> "MoneyModel":
        return await db.get(MoneyModel, user=user) or await db.add(
            MoneyModel(user=user, amount=0)
        )
