import pytest

from nook.core.initializer import (
    initialize_project,
    ProjectAlreadyExistsError,
)


def test_initializer_existing_project(tmp_path):
    project = tmp_path / "MyProject"

    (project / ".nook").mkdir(parents=True)

    with pytest.raises(ProjectAlreadyExistsError):
        initialize_project(project)


def test_initializer_creates_project(tmp_path):
    project = tmp_path / "MyProject"

    project.mkdir(parents = True)
    config_path = project / ".nook" / "config.toml"
    

    assert initialize_project(project) == project
    assert (project / ".nook").is_dir()
    assert config_path.is_file()
    assert 'name = "MyProject"' in config_path.read_text()
    assert 'version = "1"' in config_path.read_text()


def test_initializer_nested(tmp_path):
    project = tmp_path / "MyProject"
    nested = project / "A" / "backend"

    (project/ ".nook").mkdir(parents = True)
    nested.mkdir(parents=True)

    with pytest.raises(ProjectAlreadyExistsError):
        initialize_project(nested)
