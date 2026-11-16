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



def initialize_project(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()

    if not current.is_dir():
        raise NotADirectoryError(f"{current} is not a directory.")

    try:
        find_project_root(current)
    except ProjectNotFoundError:
        pass
    else:
        raise ProjectAlreadyExistsError(
            "A Nook project already exists in this directory "
            "or one of its parent directories."
        )

    nook_dir = current / ".nook"
    nook_dir.mkdir(exist_ok=False)

    slug = re.sub(
        r"[^a-z0-9]+",
        "_",
        current.name.lower()
    ).strip("_") or "project"

    schema_name = f"nook_{slug[:42]}_{uuid4().hex[:8]}"

    config_path = nook_dir / "config.toml"

    config_content = (
        "[project]\n"
        f"name = {json.dumps(current.name)}\n"
        'version = "1"\n'
        f'schema = "{schema_name}"\n'
    )

    try:
        config_path.write_text(config_content, encoding="utf-8")

        engine = get_engine()

        try:
            create_project_schema(engine, schema_name)
        finally:
            engine.dispose()

    except Exception:
        import shutil
        shutil.rmtree(nook_dir, ignore_errors=True)
        raise

    return current

            


    