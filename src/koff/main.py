import typer
from rich.console import Console
from . import core

app = typer.Typer(help="koff - AI Project Scaffolder", add_completion=False)
console = Console()

@app.command()
def scaffold(
    source: str = typer.Argument(..., help="Source to scaffold from (local path or github repo)"),
    destination: str = typer.Argument(".", help="Target directory to create the project in"),
):
    """
    Scaffold a new project from a local template or a GitHub repository.
    """
    try:
        core.scaffold_project(source, destination)
        console.print(f"[bold green]Successfully scaffolded from {source} into {destination}![/]")
    except Exception as e:
        console.print(f"[bold red]Error:[/] {e}")
        raise typer.Exit(code=1)

@app.command()
def ai(
    destination: str = typer.Argument(".", help="Target directory to inject AI configs"),
):
    """
    Inject standard AI coding assistant context files (AGENTS.md, .agents, etc.) into the target directory.
    """
    try:
        core.inject_ai_configs(destination)
        console.print(f"[bold green]Successfully injected standard AI configs into {destination}![/]")
    except Exception as e:
        console.print(f"[bold red]Error:[/] {e}")
        raise typer.Exit(code=1)

# Alias for `koff <source>` to run `scaffold` directly.
# Typer doesn't natively support this well without a custom `click` group or default callback,
# but we can implement a custom callback that catches the default case.
import sys

# Remove the callback
# @app.callback(invoke_without_command=True) ...

def _main():
    if len(sys.argv) > 1 and sys.argv[1] not in {"scaffold", "ai", "--help", "-h", "--version"}:
        sys.argv.insert(1, "scaffold")
    app()

if __name__ == "__main__":
    _main()
