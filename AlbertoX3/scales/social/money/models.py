from sqlalchemy import Column, Integer, BigInteger

from AlbertoX3.database import Base, db


class MoneyModel(Base):
    __tablename__ = "money"

    id: Column | int = Column(
        Integer, primary_key=True, unique=True, autoincrement=True, nullable=False
    )
    user: Column | int = Column(BigInteger, unique=True, nullable=False)
    amount: Column | int = Column(Integer, nullable=False)

    @staticmethod
    async def update(
        user: int,
        amount: int,
        relative: bool = False,
    ) -> "MoneyModel":
        inv = await MoneyModel.get(user)
        if relative:
            amount = inv.amount + amount
        inv.amount = amount
        return inv

    @staticmethod
    async def get(
        user: int,
    ) -> "MoneyModel":
        return await db.get(MoneyModel, user=user) or await db.add(
            MoneyModel(user=user, amount=0)
        )
