from pathlib import Path  # noqa: I001

import pytest

from nook.core.project import (
    find_project_root,
    get_current_scope,
    ProjectNotFoundError,
)

from nook.core.context import get_project_context


def test_find_project_root(tmp_path):
    project = tmp_path / "MyProject"
    nested = project / "A" / "backend"

    (project / ".nook").mkdir(parents=True)
    nested.mkdir(parents=True)

    assert find_project_root(nested) == project


def test_find_project_root_not_found(tmp_path):
    with pytest.raises(ProjectNotFoundError):
        find_project_root(tmp_path)


def test_get_current_scope(tmp_path):
    project = tmp_path / "MyProject"
    nested = project / "A" / "backend"

    project.mkdir()
    nested.mkdir(parents=True)

    assert get_current_scope(project, project) == Path(".")
    assert get_current_scope(project, nested) == Path("A/backend")


def test_get_project_context(tmp_path):
    project = tmp_path / "MyProject"
    nested = project / "A" / "backend"

    (project / ".nook").mkdir(parents=True)
    nested.mkdir(parents=True)

    context = get_project_context(nested)

    assert context.root == project
    assert context.scope == Path("A/backend")
    assert context.config_path == project / ".nook" / "config.toml"

def test_get_current_scope_outside_project(tmp_path):
    project = tmp_path / "MyProject"
    outside = tmp_path / "OtherFolder"

    project.mkdir()
    outside.mkdir()

    with pytest.raises(ProjectNotFoundError):
        get_current_scope(project, outside)


