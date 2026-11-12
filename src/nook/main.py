import typer
from nook.core.initializer import (
    initialize_project,
    ProjectAlreadyExistsError
)

app = typer.Typer(
    name="nook",
    help="A folder-specific task manager.",
    no_args_is_help=True,
)


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
     

if __name__ == "__main__":
    app()
