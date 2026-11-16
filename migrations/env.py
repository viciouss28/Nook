from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

from nook.db.base import Base
from nook.db.engine import get_engine
from nook.core.project import find_project_root
from nook.core.config import load_project_config
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
project_root = find_project_root()
project_config = load_project_config(project_root)

# Set the default schema before importing ORM models.
Base.metadata.schema = project_config.schema

# Import models so they register with Base.metadata.
from nook.models.task import Task

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def include_name(name, type_, parent_names):
    """Restrict Alembic inspection to the active project schema."""

    if type_ == "schema":
        return name == project_config.schema

    return True

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against the active Nook project schema."""

    engine = get_engine()

    try:
        with engine.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                version_table="alembic_version",
                version_table_schema=project_config.schema,
                include_schemas=True,
                include_name=include_name,
            )

            with context.begin_transaction():
                context.run_migrations()

    finally:
        engine.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
