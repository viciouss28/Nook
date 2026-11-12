from pathlib import Path
import re
from uuid import uuid4
import json

from nook.core.project import find_project_root, ProjectNotFoundError
from nook.db.engine import get_engine
from nook.db.schema import create_project_schema


class ProjectAlreadyExistsError(Exception):
    """Raised when a Nook project already exists in the current directory or an ancestor."""    
    pass


def initialize_project(start : Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    if not current.is_dir():
        raise NotADirectoryError(f"{current} is not a directory.")

        
    try:
        find_project_root(current)
    except ProjectNotFoundError:
        nook_dir = current / ".nook"
        nook_dir.mkdir(exist_ok=False)

        config_path = nook_dir / "config.toml"
        slug = re.sub(r"[^a-z0-9]+", "_", current.name.lower()).strip("_")
        
        if not slug:
            slug = "project"
        
        schema_name = f"nook_{slug[:42]}_{uuid4().hex[:8]}"
        
        config_content = (
            f'[project]\n'
            f'name = "{current.name}"\n'
            f'version = "1"\n'
            f'schema = "{schema_name}"\n'
        )

        config_path.write_text(config_content, encoding="utf-8")
        
        
        return current
    else:
        raise ProjectAlreadyExistsError(
            "A Nook project already exists in this directory or one of its parent directories."
        )
            


    