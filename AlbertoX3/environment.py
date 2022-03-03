__all__ = (
    "TOKEN",
    "LOG_LEVEL",
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
    "CACHE_TTL",
    "REDIS_HOST",
    "REDIS_PORT",
    "REDIS_DB",
    "REDIS_PASSWORD",
)


from dotenv import load_dotenv
from os import environ, getenv

from .utils import get_bool


load_dotenv()


TOKEN = environ["TOKEN"]

LOG_LEVEL = environ.get("LOG_LEVEL", "NOTSET")
if LOG_LEVEL.isnumeric():
    LOG_LEVEL = int(LOG_LEVEL)

DB_DRIVER = getenv("DB_DRIVER", "mysql+aiomysql")
DB_HOST = getenv("DB_HOST", "localhost")
DB_PORT = int(getenv("DB_PORT", 3306))
DB_DATABASE = getenv("DB_DATABASE", "AlbertoX3")

DB_USERNAME = getenv("DB_USERNAME", "AlbertoX3")
DB_PASSWORD = getenv("DB_PASSWORD", "AlbertoX3")

DB_POOL_RECYCLE = int(getenv("DB_POOL_RECYCLE", 300))
DB_POOL_SIZE = int(getenv("DB_POOL_SIZE", 20))
DB_POOL_MAX_OVERFLOW = int(getenv("DB_POOL_MAX_OVERFLOW", 20))

DB_SHOW_SQL_STATEMENTS = get_bool(getenv("DB_SHOW_SQL_STATEMENTS", False))

CACHE_TTL = int(getenv("CACHE_TTL", 3600))

REDIS_HOST = getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(getenv("REDIS_PORT", 6379))
REDIS_DB = int(getenv("REDIS_DB", 0))
REDIS_PASSWORD = getenv("REDIS_PASSWORD", "")
