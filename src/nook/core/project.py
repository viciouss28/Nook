from pathlib import Path

class ProjectNotFoundError(Exception):
    """Raised when no nook project is found."""
    pass

def find_project_root(start : Path | None = None) -> Path :
    """ Find the nearest directory containing .nook."""

    current = (start or Path.cwd()).resolve()

    while True:
        nook_dir = current / ".nook"

        if nook_dir.is_dir():
            return current

        if current == current.parent:
                    raise ProjectNotFoundError(
                        "No Nook project found. Run 'nook init' first."
                    )

        current = current.parent

def get_current_scope(project_root : Path, current_dir: Path | None = None) -> Path:
    """Get the current directory relative to the project root"""

    current = (current_dir or Path.cwd()).resolve()
    root = project_root.resolve()

    try:
        return current.relative_to(root)
    except ValueError:
        raise ProjectNotFoundError("Current working directory is outside the Nook Project.")

    