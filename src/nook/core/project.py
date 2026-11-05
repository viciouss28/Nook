from pathlib import Path



def find_project_root(start : Path | None = None) -> Path | None:
    """ Find the nearest directory containing .nook."""

    current = (start or Path.cwd()).resolve()

    while True:
        nook_dir = current / ".nook"

        if nook_dir.is_dir():
            return current

        if current == current.parent:
            return None

        current = current.parent

def get_current_scope(project_root : Path, current_dir: Path | None = None) -> Path:
    """Get the current directory relative to the project root"""

    current = (current_dir or Path.cwd()).resolve()
    root = project_root.resolve()

    return current.relative_to(root)

    