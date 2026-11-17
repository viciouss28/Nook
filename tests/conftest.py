import pytest
from uuid import uuid4

from unittest.mock import MagicMock
from contextlib import contextmanager


@pytest.fixture
def mock_db(monkeypatch):
    db = MagicMock()

    @contextmanager
    def mock_session():
        yield db

    monkeypatch.setattr(
        "nook.main.get_session_factory",
        lambda: mock_session
    )

    return db
    
@pytest.fixture
def unique_title():
    return lambda prefix="Test task": f"{prefix} {uuid4()}"