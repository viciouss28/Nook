from dataclasses import dataclass
from pathlib import Path

from nook.core.project import find_project_root, get_current_scope


@dataclass(frozen=True)
class ProjectContext:
    root : Path
    scope : Path
    config_path : Path


def get_project_context(
    start: Path | None = None
) -> ProjectContext:

    current = (start or Path.cwd()).resolve()

    root = find_project_root(current)

    scope = get_current_scope(root,current)

    config_path = root / ".nook" / "config.toml"

    return ProjectContext(
        root=root,
        scope=scope,
        config_path=config_path
    )
