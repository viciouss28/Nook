from uuid import uuid4
from nook.core.project import find_project_root, get_current_scope
from nook.db.session import get_session_factory
from nook.repositories.task_repo import TaskRepository
import pytest
from unittest.mock import Mock, call

def test_create_task():
    project_root = find_project_root()
    scope = get_current_scope(project_root)

    SessionLocal = get_session_factory()

    with SessionLocal() as db:
        repository = TaskRepository(db)

        task = repository.create_task(
            title="Complete Nook",
            description="Build the CLI task manager",
            scope_path=scope.as_posix(),
        )

        assert task.id is not None
        assert task.title == "Complete Nook"
        assert task.status == "pending"
        assert task.scope_path == scope.as_posix()
        assert task.created_at is not None
        assert task.updated_at is not None


def test_get_task():
    SessionLocal = get_session_factory()

    with SessionLocal() as db:
        repository = TaskRepository(db)

        task = repository.create_task(
            title="Test retrieval",
            scope_path="."
        )

        result = repository.get_task(task.id)

        assert result is not None
        assert result.id == task.id
        assert result.title == "Test retrieval"


def test_get_tasks_exact_scope():
    SessionLocal = get_session_factory()

    with SessionLocal() as db:
        repository = TaskRepository(db)

        repository.create_task("Root task", ".")
        repository.create_task("Backend task", "A/backend")

        tasks = repository.get_tasks(".")

        assert all(task.scope_path == "." for task in tasks)


def test_get_tasks_recursive():
    SessionLocal = get_session_factory()

    with SessionLocal() as db:
        repository = TaskRepository(db)

        repository.create_task("Root task", ".")
        repository.create_task("Backend task", "A/backend")
        repository.create_task("Frontend task", "B/frontend")

        tasks = repository.get_tasks(".", recursive=True)

        scopes = {task.scope_path for task in tasks}

        assert "." in scopes
        assert "A/backend" in scopes
        assert "B/frontend" in scopes

def test_update_task():
    SessionLocal = get_session_factory()

    with SessionLocal() as db:
        repository = TaskRepository(db)

        task = repository.create_task(
            title="Original title",
            description="Original description",
            scope_path="."
        )

        updated = repository.update_task(
            task_id=task.id,
            title="Updated title",
            description="Updated description"
        )

        assert updated is not None
        assert updated.title == "Updated title"
        assert updated.description == "Updated description"


def test_update_nonexistent_task():
    SessionLocal = get_session_factory()

    with SessionLocal() as db:
        repository = TaskRepository(db)

        result = repository.update_task(task_id=-1)

        assert result is None

def test_complete_task():
    SessionLocal = get_session_factory()

    with SessionLocal() as db:
        repository = TaskRepository(db)

        task = repository.create_task(
            title="Complete by ID",
            scope_path="."
        )

        completed = repository.complete_task(task.id)

        assert completed is not None
        assert completed.status == "completed"

def test_complete_task_by_title():
    SessionLocal = get_session_factory()

    with SessionLocal() as db:
        repository = TaskRepository(db)

        repository.create_task(
            title="Complete by title",
            scope_path="."
        )

        completed = repository.complete_task_by_title(
            title="Complete by title",
            scope_path="."
        )

        assert completed is not None
        assert completed.status == "completed"

def test_complete_task_by_title_not_found():
    SessionLocal = get_session_factory()

    with SessionLocal() as db:
        repository = TaskRepository(db)

        result = repository.complete_task_by_title(
            title="Nonexistent task",
            scope_path="."
        )

        assert result is None

def test_delete_task():
    SessionLocal = get_session_factory()

    with SessionLocal() as db:
        repository = TaskRepository(db)

        task = repository.create_task(
            title="Task to delete",
            scope_path="."
        )

        result = repository.delete_task(task.id)

        assert result is True
        assert repository.get_task(task.id) is None

def test_delete_nonexistent_task():
    SessionLocal = get_session_factory()

    with SessionLocal() as db:
        repository = TaskRepository(db)

        result = repository.delete_task(-1)

        assert result is False

def test_get_tasks_by_title():
    SessionLocal = get_session_factory()

    with SessionLocal() as db:
        repository = TaskRepository(db)

        title = f"Fix login bug {uuid4()}"

        repository.create_task(title, ".")
        repository.create_task(title, ".")
        repository.create_task(title, "backend")

        tasks = repository.get_tasks_by_title(
            title=title,
            scope_path="."
        )

        assert len(tasks) == 2
        assert all(task.title == title for task in tasks)


def test_create_duplicate_task_allowed():
    SessionLocal = get_session_factory()

    with SessionLocal() as db:
        repository = TaskRepository(db)

        title = f"Fix login bug {uuid4()}"

        task1 = repository.create_task(title, ".")
        task2 = repository.create_task(title, ".")

        assert task1.id != task2.id
        assert task1.title == task2.title


def test_delete_all_tasks_exact_scope():
    SessionLocal = get_session_factory()

    with SessionLocal() as db:
        repository = TaskRepository(db)

        scope = f"test-{uuid4()}"
        child_scope = f"{scope}/backend"

        repository.create_task("Task 1", scope)
        repository.create_task("Task 2", scope)
        child_task = repository.create_task("Child task", child_scope)

        count = repository.delete_all_tasks(
            scope_path=scope,
            recursive=False
        )

        assert count == 2
        assert repository.get_tasks(scope) == []
        assert repository.get_task(child_task.id) is not None

def test_delete_all_tasks_empty_scope():
    SessionLocal = get_session_factory()

    with SessionLocal() as db:
        repository = TaskRepository(db)

        scope = f"empty-{uuid4()}"

        count = repository.delete_all_tasks(
            scope_path=scope,
            recursive=False
        )

        assert count == 0  


def test_delete_all_tasks_recursive():
    db = Mock()

    task1 = object()
    task2 = object()

    db.scalars.return_value.all.return_value = [task1, task2]

    repository = TaskRepository(db)

    count = repository.delete_all_tasks(
        scope_path=".",
        recursive=True
    )

    assert count == 2

    db.delete.assert_has_calls([
        call(task1),
        call(task2)
    ])

    db.commit.assert_called_once()


def test_get_task_stats_exact_scope():
    SessionLocal = get_session_factory()

    with SessionLocal() as db:
        repository = TaskRepository(db)

        scope = f"stats-{uuid4()}"

        repository.create_task("Pending 1", scope)
        repository.create_task("Pending 2", scope)

        completed_task = repository.create_task("Completed task", scope)
        repository.complete_task(completed_task.id)

        repository.create_task("Child task", f"{scope}/backend")

        stats = repository.get_task_stats(scope_path=scope)

        assert stats == {
            "total": 3,
            "pending": 2,
            "completed": 1,
        }

def test_get_task_stats_recursive():
    SessionLocal = get_session_factory()

    with SessionLocal() as db:
        repository = TaskRepository(db)

        scope = f"stats-{uuid4()}"

        # Capture existing project-wide statistics.
        before = repository.get_task_stats(
            scope_path=scope,
            recursive=True
        )

        repository.create_task("Root task", scope)
        repository.create_task("Child task", f"{scope}/backend")

        completed_task = repository.create_task(
            "Completed child task",
            f"{scope}/frontend"
        )
        repository.complete_task(completed_task.id)

        after = repository.get_task_stats(
            scope_path=scope,
            recursive=True
        )

        assert after["total"] == before["total"] + 3
        assert after["pending"] == before["pending"] + 2
        assert after["completed"] == before["completed"] + 1