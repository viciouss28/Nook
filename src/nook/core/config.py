
import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectConfig:
    name: str
    version: str
    schema: str


def load_project_config(project_root: Path) -> ProjectConfig:
    """Load and validate the Nook project configuration."""

    config_path = project_root / ".nook" / "config.toml"

    with config_path.open("rb") as file:
        data = tomllib.load(file)

    project = data.get("project")

    if not isinstance(project, dict):
        raise ValueError("Invalid Nook configuration: missing [project] section.")

    name = project.get("name")
    version = project.get("version")
    schema = project.get("schema")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Invalid project name in config.toml.")

    if not isinstance(version, str) or not version.strip():
        raise ValueError("Invalid project version in config.toml.")
    
    if not isinstance(schema, str) or not schema.strip():
        raise ValueError("Invalid project schema in config.toml.")
        
    return ProjectConfig(
        name=name,
        version=version,
        schema=schema
    )
