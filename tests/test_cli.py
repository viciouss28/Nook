from typer.testing import CliRunner
from nook.main import app
import pytest

runner = CliRunner()

def test_init_command(tmp_path,monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["init"])

    assert result.exit_code == 0
    assert (tmp_path / ".nook").is_dir()
    assert (tmp_path / ".nook" / "config.toml").is_file()

def test_init_command_existing_project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    (tmp_path / ".nook").mkdir(parents=True)

    result = runner.invoke(app,["init"])

    assert result.exit_code == 1
    assert "A Nook project already exists" in result.output
    

def test_add_command(tmp_path, monkeypatch, mock_db, unique_title):
    monkeypatch.chdir(tmp_path)

    from unittest.mock import MagicMock

    task = MagicMock()
    task.id = 101
    task.title = unique_title()

    mock_db.add.return_value = None

    from nook.repositories.task_repo import TaskRepository

    monkeypatch.setattr(
        TaskRepository,
        "create_task",
        lambda self, title, scope_path, description=None: task
    )

    from nook.core.context import ProjectContext

    # Create a temporary Nook project.
    (tmp_path / ".nook").mkdir()
    (tmp_path / ".nook" / "config.toml").write_text(
        '[project]\nname = "test"\nversion = "0.1.0"\nschema = "nook_test"\n'
    )

    result = runner.invoke(app, ["add", task.title])

    assert result.exit_code == 0
    assert "Task created successfully" in result.output
    assert "101" in result.output


def test_get_command(tmp_path, monkeypatch, mock_db):
    from unittest.mock import MagicMock
    from nook.repositories.task_repo import TaskRepository

    monkeypatch.chdir(tmp_path)

    (tmp_path / ".nook").mkdir()
    (tmp_path / ".nook" / "config.toml").write_text(
        '[project]\nname = "test"\nversion = "0.1.0"\nschema = "nook_test"\n'
    )

    task = MagicMock()
    task.id = 101
    task.title = "Test task"
    task.description = "Testing get command"
    task.status = "pending"
    task.scope_path = "."

    monkeypatch.setattr(
        TaskRepository,
        "get_tasks",
        lambda self, scope_path, recursive=False: [task]
    )

    result = runner.invoke(app, ["get"])

    assert result.exit_code == 0
    assert "Test task" in result.output
    assert "101" in result.output

def test_get_recursive_command(tmp_path, monkeypatch, mock_db):
    from nook.repositories.task_repo import TaskRepository

    monkeypatch.chdir(tmp_path)

    (tmp_path / ".nook").mkdir()
    (tmp_path / ".nook" / "config.toml").write_text(
        '[project]\nname = "test"\nversion = "0.1.0"\nschema = "nook_test"\n'
    )

    tasks = []

    for task_id, title, scope in [
        (101, "Root task", "."),
        (102, "Backend task", "src/backend"),
    ]:
        task = type("Task", (), {
            "id": task_id,
            "title": title,
            "description": None,
            "status": "pending",
            "scope_path": scope,
        })()
        tasks.append(task)

    monkeypatch.setattr(
        TaskRepository,
        "get_tasks",
        lambda self, scope_path, recursive=False: tasks
    )

    result = runner.invoke(app, ["get", "-r"])

    assert result.exit_code == 0
    assert "Root task" in result.output
    assert "Backend task" in result.output

def test_update_command(tmp_path, monkeypatch, mock_db):
    from nook.repositories.task_repo import TaskRepository

    monkeypatch.chdir(tmp_path)

    (tmp_path / ".nook").mkdir()
    (tmp_path / ".nook" / "config.toml").write_text(
        '[project]\nname = "test"\nversion = "0.1.0"\nschema = "nook_test"\n'
    )

    task = type("Task", (), {
        "id": 101,
        "title": "Updated title",
        "description": "Updated description",
        "status": "pending",
    })()

    monkeypatch.setattr(
        TaskRepository,
        "update_task",
        lambda self, task_id, title=None, description=None: task
    )

    result = runner.invoke(
        app,
        ["update", "101", "--title", "Updated title"]
    )

    assert result.exit_code == 0
    assert "Task updated successfully" in result.output
    assert "Updated title" in result.output
    assert "Updated description" in result.output

def test_complete_command(tmp_path, monkeypatch, mock_db):
    from nook.services.task_service import TaskService

    monkeypatch.chdir(tmp_path)

    (tmp_path / ".nook").mkdir()
    (tmp_path / ".nook" / "config.toml").write_text(
        '[project]\nname = "test"\nversion = "0.1.0"\nschema = "nook_test"\n'
    )

    from nook.services.task_service import TaskActionResult

    monkeypatch.setattr(
        TaskService,
        "complete_tasks_by_ids",
        lambda self, task_ids: [
            TaskActionResult(
                identifier=101,
                status="completed"
            )
        ]
    )

    result = runner.invoke(app, ["complete", "101"])

    assert result.exit_code == 0
    assert "101" in result.output
    assert "Completed" in result.output

def test_delete_command(tmp_path, monkeypatch, mock_db):
    from nook.services.task_service import TaskService
    from nook.services.task_service import TaskActionResult

    monkeypatch.chdir(tmp_path)

    (tmp_path / ".nook").mkdir()
    (tmp_path / ".nook" / "config.toml").write_text(
        '[project]\nname = "test"\nversion = "0.1.0"\nschema = "nook_test"\n'
    )

    monkeypatch.setattr(
        TaskService,
        "delete_tasks_by_ids",
        lambda self, task_ids: [
            TaskActionResult(
                identifier=101,
                status="deleted"
            )
        ]
    )

    result = runner.invoke(app, ["delete", "101"])

    assert result.exit_code == 0
    assert "101" in result.output
    assert "Deleted" in result.output


def test_delete_all_cancelled(tmp_path, monkeypatch, mock_db):
    from nook.repositories.task_repo import TaskRepository

    monkeypatch.chdir(tmp_path)

    (tmp_path / ".nook").mkdir()
    (tmp_path / ".nook" / "config.toml").write_text(
        '[project]\nname = "test"\nversion = "0.1.0"\nschema = "nook_test"\n'
    )

    task = type("Task", (), {"id": 101})()

    monkeypatch.setattr(
        TaskRepository,
        "get_tasks",
        lambda self, scope_path, recursive=False: [task]
    )

    result = runner.invoke(app, ["delete", "--all"], input="n\n")

    assert "permanently delete 1 tasks" in result.output
    assert "Deletion cancelled" in result.output
    mock_db.commit.assert_not_called()

def test_delete_all_with_yes(tmp_path, monkeypatch, mock_db):
    from nook.repositories.task_repo import TaskRepository

    monkeypatch.chdir(tmp_path)

    (tmp_path / ".nook").mkdir()
    (tmp_path / ".nook" / "config.toml").write_text(
        '[project]\nname = "test"\nversion = "0.1.0"\nschema = "nook_test"\n'
    )

    tasks = [
        type("Task", (), {"id": 101})(),
        type("Task", (), {"id": 102})(),
    ]

    monkeypatch.setattr(
        TaskRepository,
        "get_tasks",
        lambda self, scope_path, recursive=False: tasks
    )

    monkeypatch.setattr(
        TaskRepository,
        "delete_all_tasks",
        lambda self, scope_path, recursive=False: 2
    )

    result = runner.invoke(app, ["delete", "--all", "--yes"])

    assert result.exit_code == 0
    assert "permanently delete 2 tasks" in result.output
    assert "Successfully deleted 2 tasks" in result.output

def test_status_command(tmp_path, monkeypatch, mock_db):
    from nook.repositories.task_repo import TaskRepository

    monkeypatch.chdir(tmp_path)

    (tmp_path / ".nook").mkdir()
    (tmp_path / ".nook" / "config.toml").write_text(
        '[project]\nname = "test"\nversion = "0.1.0"\nschema = "nook_test"\n'
    )

    monkeypatch.setattr(
        TaskRepository,
        "get_task_stats",
        lambda self, scope_path, recursive=False: {
            "total": 10,
            "pending": 6,
            "completed": 4,
        }
    )

    result = runner.invoke(app, ["status"])

    assert result.exit_code == 0
    assert "Total Tasks" in result.output
    assert "Pending" in result.output
    assert "Completed" in result.output
    assert "40.0%" in result.output

def test_status_recursive_command(tmp_path, monkeypatch, mock_db):
    from nook.repositories.task_repo import TaskRepository

    monkeypatch.chdir(tmp_path)

    (tmp_path / ".nook").mkdir()
    (tmp_path / ".nook" / "config.toml").write_text(
        '[project]\nname = "test"\nversion = "0.1.0"\nschema = "nook_test"\n'
    )

    def mock_stats(self, scope_path, recursive=False):
        assert recursive is True

        return {
            "total": 20,
            "pending": 12,
            "completed": 8,
        }

    monkeypatch.setattr(
        TaskRepository,
        "get_task_stats",
        mock_stats
    )

    result = runner.invoke(app, ["status", "-r"])

    assert result.exit_code == 0
    assert "Total Tasks" in result.output
    assert "20" in result.output
    assert "40.0%" in result.output