
import os
import re
from functools import lru_cache

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from nook.core.project import find_project_root
from nook.core.config import load_project_config


load_dotenv()


@lru_cache(maxsize=None)
def _create_engine(db_url: str, schema: str) -> Engine:
    """Create an engine configured for a specific Nook schema."""

    return create_engine(
        db_url,
        pool_pre_ping=True,
        connect_args={
            "options": f"-c search_path={schema},public"
        },
    )


def get_engine() -> Engine:
    """Return an engine configured for the active Nook project."""

    db_url = os.getenv("NOOK_DATABASE_URL")

    if not db_url:
        raise RuntimeError("NOOK_DATABASE_URL is not configured.")

    project_root = find_project_root()
    config = load_project_config(project_root)

    if not re.fullmatch(r"[a-z_][a-z0-9_]{0,62}", config.schema):
        raise ValueError(f"Invalid PostgreSQL schema: {config.schema}")

    return _create_engine(db_url, config.schema)


def test_connection(engine: Engine) -> bool:
    """Check whether the database connection works."""

    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return result.scalar() == 1
