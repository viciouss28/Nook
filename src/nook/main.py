import typer

app = typer.Typer(
    name="nook",
    help="A folder-specific task manager.",
    no_args_is_help=True,
)


@app.command()
def version():
    """Display the current Nook version."""
    typer.echo("Nook v0.1.0")


if __name__ == "__main__":
    app()
