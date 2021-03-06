from __future__ import annotations


__all__ = (
    "select",
    "filter_by",
    "exists",
    "delete",
    "Base",
    "UTCDatetime",
    "DB",
    "db_context",
    "db_wrapper",
    "get_database",
    "db",
    "redis",
)


from aioredis import Redis
from asyncio import Event
from contextlib import asynccontextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
from functools import wraps, partial
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.engine import URL
from sqlalchemy.future import select as sa_select, Select
from sqlalchemy.orm import selectinload, DeclarativeMeta, registry
from sqlalchemy.sql import Executable
from sqlalchemy.sql.expression import exists as sa_exists, delete as sa_delete, Delete
from sqlalchemy.sql.functions import count
from sqlalchemy.sql.selectable import Exists
from sqlalchemy import TypeDecorator, DateTime, Table
from typing import TYPE_CHECKING, TypeVar, Type

from AlbertUnruhUtils.utils.logger import get_logger

from .environment import (
    DB_DRIVER,
    DB_HOST,
    DB_PORT,
    DB_DATABASE,
    DB_USERNAME,
    DB_PASSWORD,
    DB_POOL_RECYCLE,
    DB_POOL_SIZE,
    DB_POOL_MAX_OVERFLOW,
    DB_SHOW_SQL_STATEMENTS,
    REDIS_DB,
    REDIS_HOST,
    REDIS_PORT,
    REDIS_PASSWORD,
)


if TYPE_CHECKING:
    from typing import Optional, Any, NoReturn


T = TypeVar("T")
logger = get_logger(__name__.split(".")[-1], level=None, add_handler=False)


redis: Redis = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
)


# Note:
# this file is "inspired" by https://github.com/PyDrocsid/library/blob/develop/PyDrocsid/database.py


def select(entity, *args) -> Select:
    if not args:
        return sa_select(entity)

    options = []
    for arg in args:
        if isinstance(arg, (tuple, list)):
            head, *tail = arg
            opt = selectinload(head)
            for t in tail:
                opt = opt.selectinload(t)
            options.append(opt)
        else:
            options.append(selectinload(arg))

    return sa_select(entity).options(*options)


def filter_by(cls, *args, **kwargs) -> Select:
    return select(cls, *args).filter_by(**kwargs)


def exists(*entities, **kwargs) -> Exists:
    return sa_exists(*entities, **kwargs)


def delete(table) -> Delete:
    return sa_delete(table)


class Base(metaclass=DeclarativeMeta):
    __table__: Table
    __tablename__: str
    __abstract__ = True
    registry = registry()
    metadata = registry.metadata

    __table_args__ = {"mysql_collate": "utf8mb4_bin"}

    def __init__(self, **kwargs: Any):
        self.registry.constructor(self, **kwargs)


class UTCDatetime(TypeDecorator):
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return value.replace(tzinfo=timezone.utc)

    def process_literal_param(self, value, dialect):
        raise NotImplementedError

    def python_type(self):
        return datetime


class DB:
    """
    A database connection.
    """

    engine: AsyncEngine
    _session: ContextVar[Optional[AsyncSession]]
    _close_event: ContextVar[Optional[Event]]

    def __init__(
        self,
        driver: str,
        host: str,
        port: int,
        database: str,
        username: str,
        password: str,
        pool_recycle: int = 300,
        pool_size: int = 20,
        max_overflow: int = 20,
        echo: bool = False,
    ):
        """
        Parameters
        ----------
        driver: str
            The SQL connection driver.
        host: str
            Host of the SQL server.
        port: int
            Port of the SQL server.
        database: str
            Name of the database.
        username: str
            Username to use for the database.
        password: str
            Password to use for the database.
        pool_recycle: int
            The amount of seconds to wait to recycle a connection pool.
        pool_size: int
            The size of the connection pool.
        max_overflow: int
            The max amount of connections to allow over the pool.
        echo: bool
            Whether SQL queries should be logged or not.
        """
        self.engine = create_async_engine(
            URL.create(
                drivername=driver,
                username=username,
                password=password,
                host=host,
                port=port,
                database=database,
            ),
            pool_pre_ping=True,
            pool_recycle=pool_recycle,
            pool_size=pool_size,
            max_overflow=max_overflow,
            echo=echo,
        )

        self._session = ContextVar("session", default=None)
        self._close_event = ContextVar("close_event", default=None)

    async def create_tables(self) -> NoReturn:
        """
        Creates all tables for the scales.
        """
        tables = [d.__table__ for d in Base.__subclasses__()]  # type: ignore

        logger.debug(
            f"Creating following tables (if they don't exist): "
            f"{', '.join(map(lambda t: t.name, tables))}"
        )

        async with self.engine.begin() as conn:
            await conn.run_sync(partial(Base.metadata.create_all, tables=tables))

    async def add(self, obj: T) -> T:
        self.session.add(obj)
        return obj

    async def delete(self, obj: T) -> T:
        await self.session.delete(obj)
        return obj

    async def exec(self, statement: Executable, *args, **kwargs):
        return await self.session.execute(statement, *args, **kwargs)

    async def stream(self, statement: Executable, *args, **kwargs):
        return (await self.session.stream(statement, *args, **kwargs)).scalars()

    async def all(self, statement: Executable, *args, **kwargs):
        return [x async for x in await self.stream(statement, *args, **kwargs)]

    async def first(self, statement: Executable, *args, **kwargs):
        return (await self.exec(statement, *args, **kwargs)).scalar()

    async def exists(self, *args, **kwargs):
        return await self.first(exists(*args, **kwargs).select())

    async def count(self, *args, **kwargs):
        return await self.first(select(count()).select_from(*args, **kwargs))

    async def get(self, cls: Type[T], *args, **kwargs) -> T | None:
        return await self.first(filter_by(cls, *args, **kwargs))

    async def commit(self) -> NoReturn:
        if self._session.get():
            await self.session.commit()

    async def close(self) -> NoReturn:
        if self._session.get():
            await self.session.close()
            self._close_event.get().set()

    def create_session(self) -> AsyncSession:
        self._session.set(session := AsyncSession(self.engine, expire_on_commit=False))
        self._close_event.set(Event())
        return session

    @property
    def session(self) -> AsyncSession:
        return self._session.get()

    async def wait_for_close_event(self):
        await self._close_event.get().wait()


@asynccontextmanager
async def db_context():
    db.create_session()
    try:
        yield
    finally:
        await db.commit()
        await db.close()


def db_wrapper(func: T) -> T:
    @wraps(func)
    async def decorator(*args, **kwargs):
        async with db_context():
            return await func(*args, **kwargs)

    return decorator


def get_database() -> DB:
    """
    Creates a database object from environment variables.
    """
    return DB(
        driver=DB_DRIVER,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_DATABASE,
        username=DB_USERNAME,
        password=DB_PASSWORD,
        pool_recycle=DB_POOL_RECYCLE,
        pool_size=DB_POOL_SIZE,
        max_overflow=DB_POOL_MAX_OVERFLOW,
        echo=DB_SHOW_SQL_STATEMENTS,
    )


db: DB = get_database()
