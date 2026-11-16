import typer
from nook.core.initializer import (
    initialize_project,
    ProjectAlreadyExistsError
)
from rich.console import Console
from rich.table import Table

from nook.core.project import (
    find_project_root,
    get_current_scope,
    ProjectNotFoundError,
)
from nook.db.session import get_session_factory
from nook.repositories.task_repo import TaskRepository
from nook.services.task_service import TaskService


app = typer.Typer(
    name="nook",
    help="A folder-specific task manager.",
    no_args_is_help=True,
)

console = Console()

@app.command()
def version():
    """Display the current Nook version."""
    typer.echo("Nook v0.1.0")

@app.command()
def init():
    """Initialize a new nook project in the current directory."""

    try:
        project_root = initialize_project()

    except ProjectAlreadyExistsError as e:
        typer.echo(f"Error : {e}", err=True)
        raise typer.Exit(code=1)

    except NotADirectoryError as e:
        typer.echo(f"Error : {e}", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"Initialized a Nook project in {project_root}")
     
@app.command()
def complete(
    task_ids: list[int] = typer.Argument(None, help="Task IDs to complete."),
    titles: list[str] = typer.Option(
        None,
        "--title",
        "-t",
        help="Task titles to complete."
    ),
):
    """Complete one or more tasks."""

    if task_ids and titles:
        typer.echo("Error: Provide either task IDs or titles, not both.", err=True)
        raise typer.Exit(code=1)

    if not task_ids and not titles:
        typer.echo("Error: Provide at least one task ID or title.", err=True)
        raise typer.Exit(code=1)

    try:
        project_root = find_project_root()
        scope_path = get_current_scope(project_root).as_posix()

    except ProjectNotFoundError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    SessionLocal = get_session_factory()

    with SessionLocal() as db:
        repository = TaskRepository(db)
        service = TaskService(repository)

        if task_ids:
            results = service.complete_tasks_by_ids(task_ids)
        else:
            results = service.complete_tasks_by_titles(titles, scope_path)

    table = Table(title="Task Completion Results")
    table.add_column("Task")
    table.add_column("Result")

    for result in results:
        table.add_row(
            str(result.identifier),
            result.status.replace("_", " ").title()
        )

    console.print(table)

@app.command()
def add(
    title: str = typer.Argument(..., help="Title of the task."),
    description: str | None = typer.Option(
        None,
        "--description",
        "-d",
        help="Optional task description."
    ),
):
    """Add a new task."""

    try:
        project_root = find_project_root()
        scope_path = get_current_scope(project_root).as_posix()

    except ProjectNotFoundError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    SessionLocal = get_session_factory()

    with SessionLocal() as db:
        repository = TaskRepository(db)

        existing_tasks = repository.get_tasks_by_title(
            title=title,
            scope_path=scope_path
        )

        if existing_tasks:
            console.print(
                f"[red]A task with the title '{title}' already exists in this folder.[/red]"
            )
            raise typer.Exit(code=1)

        task = repository.create_task(
            title=title,
            description=description,
            scope_path=scope_path
        )

    console.print(f"[green]Task created successfully![/green] ID: {task.id}")

@app.command()
def delete(
    task_ids: list[int] = typer.Argument(None, help="Task IDs to delete."),
    titles: list[str] = typer.Option(
        None,
        "--title",
        "-t",
        help="Task titles to delete."
    ),
    all_tasks: bool = typer.Option(
        False,
        "--all",
        help="Delete all tasks in the selected scope."
    ),
    recursive: bool = typer.Option(
        False,
        "--recursive",
        "-r",
        help="Include tasks from all project folders."
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Skip deletion confirmation."
    ),
):
    """Delete one or more tasks."""

    if task_ids and titles:
        typer.echo("Error: Provide either task IDs or titles, not both.", err=True)
        raise typer.Exit(code=1)
    
    if all_tasks and (task_ids or titles):
        typer.echo("Error: --all cannot be combined with task IDs or titles.", err=True)
        raise typer.Exit(code=1)
    
    if recursive and not all_tasks:
        typer.echo("Error: -r can only be used with --all.", err=True)
        raise typer.Exit(code=1)
    
    if yes and not all_tasks:
        typer.echo("Error: -y can only be used with --all.", err=True)
        raise typer.Exit(code=1)
    
    if not all_tasks and not task_ids and not titles:
        typer.echo("Error: Provide task IDs, titles, or --all.", err=True)
        raise typer.Exit(code=1)

    try:
        project_root = find_project_root()
        scope_path = get_current_scope(project_root).as_posix()

    except ProjectNotFoundError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    SessionLocal = get_session_factory()

    with SessionLocal() as db:
        repository = TaskRepository(db)
        service = TaskService(repository)
    
        if all_tasks:
            tasks = repository.get_tasks(
                scope_path=scope_path,
                recursive=recursive
            )
    
            if not tasks:
                console.print("[yellow]No tasks found to delete.[/yellow]")
                return
    
            console.print(
                f"[bold red]This will permanently delete {len(tasks)} tasks.[/bold red]"
            )
    
            if not yes:
                confirmed = typer.confirm("Are you sure you want to continue?")
    
                if not confirmed:
                    console.print("[yellow]Deletion cancelled.[/yellow]")
                    raise typer.Exit()
    
            count = repository.delete_all_tasks(
                scope_path=scope_path,
                recursive=recursive
            )
    
            console.print(f"[green]Successfully deleted {count} tasks.[/green]")
            return
    
        if task_ids:
            results = service.delete_tasks_by_ids(task_ids)
        else:
            results = service.delete_tasks_by_titles(titles, scope_path)

    table = Table(title="Task Deletion Results")
    table.add_column("Task")
    table.add_column("Result")

    for result in results:
        table.add_row(
            str(result.identifier),
            result.status.replace("_", " ").title()
        )

    console.print(table)

@app.command()
def get(
    recursive: bool = typer.Option(
        False,
        "--recursive",
        "-r",
        help="Show tasks from all folders in the project."
    )
):
    """Display tasks."""

    try:
        project_root = find_project_root()
        scope_path = get_current_scope(project_root).as_posix()

    except ProjectNotFoundError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    SessionLocal = get_session_factory()

    with SessionLocal() as db:
        repository = TaskRepository(db)

        tasks = repository.get_tasks(
            scope_path=scope_path,
            recursive=recursive
        )

    if not tasks:
        console.print("[yellow]No tasks found.[/yellow]")
        return

    table = Table(title="Your Tasks")

    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Title", style="bold")
    table.add_column("Description")
    table.add_column("Status")
    table.add_column("Folder")

    for task in tasks:
        status_style = "green" if task.status == "completed" else "yellow"

        table.add_row(
            str(task.id),
            task.title,
            task.description or "-",
            f"[{status_style}]{task.status.title()}[/{status_style}]",
            task.scope_path
        )

    console.print(table)


    
if __name__ == "__main__":
    app()
