import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


load_dotenv()

def get_engine() -> Engine:
    """Create and return a SQLAlchemy engine."""

    DB_URL = os.getenv("NOOK_DATABASE_URL")

    if not DB_URL:
        raise RuntimeError(
            "NOOK_DATABASE_URL is not configured."
        )

    engine = create_engine(
        DB_URL,
        pool_pre_ping=True,
    )

    return engine

def test_connection(engine : Engine) -> bool:
    """Checks whether the database connection works."""

    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))

        return result.scalar() == 1