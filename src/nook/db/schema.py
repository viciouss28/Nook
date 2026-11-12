
import re

from sqlalchemy.engine import Engine
from sqlalchemy.schema import CreateSchema


def create_project_schema(engine: Engine, schema_name: str) -> None:
    """Create a PostgreSQL schema for a Nook project."""

    if not re.fullmatch(r"[a-z_][a-z0-9_]{0,62}", schema_name):
        raise ValueError(f"Invalid PostgreSQL schema name: {schema_name}")

    with engine.begin() as connection:
        connection.execute(
            CreateSchema(schema_name, if_not_exists=True)
        )
