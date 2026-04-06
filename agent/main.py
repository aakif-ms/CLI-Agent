import sys
import os
from pathlib import Path
import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from dotenv import load_dotenv

load_dotenv()

app = typer.Typer(
    name="agent",
    help="🧠 Agentic PowerShell CLI Assistant — natural language → safe PowerShell",
    add_completion=False,
)
console = Console()

def _print_banner():
    """Print the startup banner."""
    banner = Text()
    banner.append("  🧠 ", style="bold")
    banner.append("Agentic PowerShell CLI Assistant", style="bold bright_white")
    banner.append("\n  Powered by LangGraph · HITL Safety · Risk Classification", style="dim")

    console.print(
        Panel(banner, border_style="bright_blue", padding=(0, 2))
    )
    
def _print_summary(state: dict):
    """Print the final run summary."""
    success = state.get("execution_success")
    denied = state.get("hitl_decision") == "denied"
    invalid = state.get("is_valid") is False

    console.print("\n" + "─" * 50)

    if invalid:
        console.print(
            f"[yellow]⚠️  Request rejected:[/yellow] {state.get('validation_reason', '')}"
        )
    elif denied:
        console.print("[yellow]⚠️  Command denied by user. Nothing was executed.[/yellow]")
    elif success:
        console.print("[bold green]✅ Done! Command executed successfully.[/bold green]")
        output = state.get("execution_output", "")
        if output and output != "[DRY RUN] Command was not executed.":
            console.print(f"[dim]Output:[/dim] {output[:500]}")
    else:
        console.print("[red]❌ Pipeline ended without successful execution.[/red]")
        expl = state.get("error_explanation", "")
        if expl:
            console.print(f"[dim]Reason:[/dim] {expl}")

    console.print("─" * 50 + "\n")

@app.command()
def main(
    request: str = typer.Argument(
        ...,
        help='Natural language PowerShell request. Example: "list all running processes"',
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show extra debug information.",
    ),
):
    """
    🧠 Convert a natural language request into a safe, approved PowerShell command.
    """

    _print_banner()
    console.print(f"\n[bold]📥 Request:[/bold] [italic]{request}[/italic]\n")

    try:
        from .graph import build_graph

        graph = build_graph()

        initial_state: dict = {
            "user_input": request,
            "is_valid": None,
            "validation_reason": None,
            "generated_command": None,
            "cmd_intent": None,
            "risk_level": None,
            "risk_reason": None,
            "explanation": None,
            "impact_summary": None,
            "hitl_decision": None,
            "edited_cmd": None,
            "execution_output": None,
            "execution_success": None,
            "error_message": None,
            "error_explanation": None,
            "suggested_fix": None,
            "retry_count": 0,
        }

        final_state = graph.invoke(initial_state)
        _print_summary(final_state)

    except EnvironmentError as e:
        console.print(f"[bold red]Configuration Error:[/bold red]\n{e}")
        raise typer.Exit(code=1)

    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠️  Interrupted by user. Exiting.[/yellow]")
        raise typer.Exit(code=0)

    except Exception as e:
        console.print(f"\n[bold red]Unexpected error:[/bold red] {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
