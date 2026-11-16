
from sqlalchemy.orm import sessionmaker, Session

from nook.db.engine import get_engine


def get_session_factory() -> sessionmaker[Session]:
    """Return a session factory for the active Nook project."""

    return sessionmaker(
        bind=get_engine(),
        autoflush=False,
        expire_on_commit=True,
    )
