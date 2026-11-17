from unittest.mock import MagicMock

from nook.services.task_service import TaskService


def test_complete_tasks_by_ids():
    repository = MagicMock()

    task1 = MagicMock()
    task2 = MagicMock()

    repository.complete_task.side_effect = [
        task1,
        None,
        task2
    ]

    service = TaskService(repository)

    results = service.complete_tasks_by_ids([1, 2, 3])

    assert len(results) == 3

    assert results[0].status == "completed"
    assert results[0].identifier == 1

    assert results[1].status == "not_found"
    assert results[1].identifier == 2

    assert results[2].status == "completed"
    assert results[2].identifier == 3

    assert repository.complete_task.call_count == 3

def test_complete_tasks_by_titles():
    repository = MagicMock()

    task1 = MagicMock()
    task1.id = 1

    task2 = MagicMock()
    task2.id = 2

    repository.get_tasks_by_title.side_effect = [
        [task1],
        [task2]
    ]

    repository.complete_task.side_effect = [task1, task2]

    service = TaskService(repository)

    results = service.complete_tasks_by_titles(
        titles=["Fix login", "Update README"],
        scope_path="."
    )

    assert len(results) == 2
    assert all(result.status == "completed" for result in results)
    assert repository.complete_task.call_count == 2


def test_complete_tasks_by_titles_ambiguous():
    repository = MagicMock()

    task1 = MagicMock()
    task2 = MagicMock()

    repository.get_tasks_by_title.return_value = [task1, task2]

    service = TaskService(repository)

    results = service.complete_tasks_by_titles(
        titles=["Fix login"],
        scope_path="."
    )

    assert results[0].status == "ambiguous"
    repository.complete_task.assert_not_called()

def test_complete_tasks_by_titles_not_found():
    repository = MagicMock()
    repository.get_tasks_by_title.return_value = []

    service = TaskService(repository)

    results = service.complete_tasks_by_titles(
        titles=["Unknown task"],
        scope_path="."
    )

    assert results[0].status == "not_found"
    repository.complete_task.assert_not_called()

def test_delete_tasks_by_ids():
    repository = MagicMock()

    repository.delete_task.side_effect = [
        True,
        False,
        True
    ]

    service = TaskService(repository)

    results = service.delete_tasks_by_ids([1, 2, 3])

    assert len(results) == 3

    assert results[0].status == "deleted"
    assert results[0].identifier == 1

    assert results[1].status == "not_found"
    assert results[1].identifier == 2

    assert results[2].status == "deleted"
    assert results[2].identifier == 3

    assert repository.delete_task.call_count == 3

def test_delete_tasks_by_titles():
    repository = MagicMock()

    task = MagicMock()
    task.id = 10

    repository.get_tasks_by_title.return_value = [task]
    repository.delete_task.return_value = True

    service = TaskService(repository)

    results = service.delete_tasks_by_titles(
        titles=["Old component"],
        scope_path="."
    )

    assert results[0].status == "deleted"
    repository.delete_task.assert_called_once_with(10)

def test_delete_tasks_by_titles_not_found():
    repository = MagicMock()
    repository.get_tasks_by_title.return_value = []

    service = TaskService(repository)

    results = service.delete_tasks_by_titles(
        titles=["Unknown task"],
        scope_path="."
    )

    assert results[0].status == "not_found"
    repository.delete_task.assert_not_called()

def test_delete_tasks_by_titles_ambiguous():
    repository = MagicMock()

    repository.get_tasks_by_title.return_value = [
        MagicMock(),
        MagicMock()
    ]

    service = TaskService(repository)

    results = service.delete_tasks_by_titles(
        titles=["Fix login"],
        scope_path="."
    )

    assert results[0].status == "ambiguous"
    repository.delete_task.assert_not_called()