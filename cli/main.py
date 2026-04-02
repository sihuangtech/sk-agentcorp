"""
SK AgentCorp — CLI Tool

Command-line interface for managing SK AgentCorp instances.
Commands: init, start, dashboard, status, heartbeat
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

app = typer.Typer(
    name="sk-agentcorp",
    help="🏢 SK AgentCorp — Zero-Human Company Operating System",
    add_completion=False,
)
console = Console()


BANNER = """
[bold cyan]
  ███████╗ █████╗  ██████╗ ██╗  ██╗██████╗  ██████╗ ██████╗ ███████╗
  ██╔════╝██╔══██╗██╔════╝██║ ██╔╝██╔══██╗██╔════╝██╔═══██╗██╔════╝
  ███████╗███████║██║     █████╔╝ ██████╔╝██║     ██║   ██║█████╗
  ╚════██║██╔══██║██║     ██╔═██╗ ██╔══██╗██║     ██║   ██║██╔══╝
  ███████║██║  ██║╚██████╗██║  ██╗██║  ██║╚██████╗╚██████╔╝███████╗
  ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝
[/bold cyan]
[dim]  Zero-Human Company Operating System[/dim]
"""


@app.command()
def init(
    directory: str = typer.Argument(".", help="Directory to initialize"),
    template: str = typer.Option("custom", help="Company template to use"),
):
    """Initialize a new SK AgentCorp project."""
    console.print(BANNER)

    target = Path(directory).resolve()
    target.mkdir(parents=True, exist_ok=True)

    # Copy .env.example if not exists
    env_example = Path(__file__).parent.parent / ".env.example"
    env_target = target / ".env"
    if env_example.exists() and not env_target.exists():
        shutil.copy(env_example, env_target)
        console.print("  [green]✓[/green] Created .env from template")

    # Create data directory
    (target / "data").mkdir(exist_ok=True)
    console.print("  [green]✓[/green] Created data/ directory")

    console.print()
    console.print(Panel(
        "[bold green]SK AgentCorp initialized![/bold green]\n\n"
        "Next steps:\n"
        "  1. Edit [cyan].env[/cyan] and add your LLM API keys\n"
        "  2. Run [cyan]sk-agentcorp start[/cyan] to start the server\n"
        "  3. Run [cyan]sk-agentcorp dashboard[/cyan] to open the dashboard",
        title="🏢 Ready",
        border_style="green",
    ))


@app.command()
def start(
    host: str = typer.Option("0.0.0.0", help="Host to bind to"),
    port: int = typer.Option(8000, help="Port to bind to"),
    reload: bool = typer.Option(False, help="Enable auto-reload for development"),
):
    """Start the SK AgentCorp backend server."""
    console.print(BANNER)
    console.print(f"  [cyan]Starting server on {host}:{port}...[/cyan]\n")

    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )


@app.command()
def dashboard():
    """Open the SK AgentCorp dashboard in your browser."""
    import webbrowser
    url = "http://localhost:5173"
    console.print(f"  [cyan]Opening dashboard at {url}[/cyan]")
    webbrowser.open(url)


@app.command()
def status():
    """Check the status of the SK AgentCorp server."""
    console.print(BANNER)

    import httpx

    try:
        response = httpx.get("http://localhost:8000/api/health", timeout=5)
        data = response.json()

        table = Table(title="SK AgentCorp Status")
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="green")

        for key, value in data.items():
            table.add_row(key, str(value))

        console.print(table)

    except Exception:
        console.print("  [red]✗ Server is not running[/red]")
        console.print("  Run [cyan]sk-agentcorp start[/cyan] to start the server")


@app.command()
def heartbeat():
    """Trigger a manual heartbeat cycle."""
    import httpx

    try:
        response = httpx.post("http://localhost:8000/api/dashboard/heartbeat/trigger", timeout=60)
        data = response.json()
        console.print(f"  [green]✓ Heartbeat triggered at {data.get('triggered_at')}[/green]")
    except Exception:
        console.print("  [red]✗ Failed to trigger heartbeat. Is the server running?[/red]")


if __name__ == "__main__":
    app()
