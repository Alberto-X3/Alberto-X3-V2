__all__ = (
    "TOKEN",
    "DB_DRIVER",
    "DB_HOST",
    "DB_PORT",
    "DB_DATABASE",
    "DB_USERNAME",
    "DB_PASSWORD",
    "DB_POOL_RECYCLE",
    "DB_POOL_SIZE",
    "DB_POOL_MAX_OVERFLOW",
    "DB_SHOW_SQL_STATEMENTS",
)

from dotenv import load_dotenv
from os import environ, getenv

from .utils import get_bool


load_dotenv()


TOKEN = environ["TOKEN"]

DB_DRIVER = getenv("DB_DRIVER", "mysql+aiomysql")
DB_HOST = getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(getenv("DB_PORT", 3306))
DB_DATABASE = getenv("DB_DATABASE", "AlbertoX3")

DB_USERNAME = getenv("DB_USERNAME", "AlbertoX3")
DB_PASSWORD = getenv("DB_PASSWORD", "AlbertoX3")

DB_POOL_RECYCLE = int(getenv("DB_POOL_RECYCLE", 300))
DB_POOL_SIZE = int(getenv("DB_POOL_SIZE", 20))
DB_POOL_MAX_OVERFLOW = int(getenv("DB_POOL_MAX_OVERFLOW", 20))

DB_SHOW_SQL_STATEMENTS = get_bool(getenv("DB_SHOW_SQL_STATEMENTS", False))
