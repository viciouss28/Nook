from sqlalchemy.orm import sessionmaker
from nook.db.engine import get_engine

def get_session_factory():
    engine = get_engine()

    sessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    return sessionLocal