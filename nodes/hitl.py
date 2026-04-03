from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from state import AgentState

console = Console()

MAX_RETRIES = 3

RISK_COLORS = {"LOW": "green", "MEDIUM": "yellow", "HIGH": "red bold"}
RISK_EMOJI = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴"}

def _build_approval_panel(state: AgentState) -> Panel:
    cmd = state.get("generated_command", "N/A")
    risk = state.get("risk_level", "MEDIUM")
    risk_reason = state.get("risk_reason", "")
    impact = state.get("impact_summary", "")

    emoji = RISK_EMOJI.get(risk, "⚪")
    color = RISK_COLORS.get(risk, "white")

    content = Text()
    content.append("Command:\n", style="bold")
    content.append(f"  {cmd}\n\n", style="bright_white")
    content.append("Risk: ", style="bold")
    content.append(f"{emoji} {risk}", style=color)
    content.append(f" — {risk_reason}\n\n", style="dim")
    content.append("Impact: ", style="bold")
    content.append(f"{impact}\n", style="italic")

    options = "\n[A] Approve   [D] Deny   [E] Edit command   [R] Re-generate"
    if risk == "HIGH":
        options += "\n\n⚠️ HIGH risk: You will need to type [bold red]   YES[/bold red] to confirm,"

    content.append(options, style="dim cyan")

    return Panel(
        content,
        title="[bold yellow]⚠️ APPROVAL REQUIRED[/bold yellow]",
        border_style="yellow",
        padding=(1, 2),
    )
    
def hitl_approval(state: AgentState) -> AgentState:
    console.print("\n[bold cyan]👤 [Node 5 / HITL][/bold cyan] Waiting for human approval...\n")

    console.print(_build_approval_panel(state))
    
    risk = state.get("risk_level", "MEDIUM")
    retry_count = state.get("retry_count", 0)

    while True:
        choice = Prompt.ask(
            "\n[bold]Your decision[/bold]",
            choices=["A", "D", "E", "R", "a", "d", "e", "r"],
            default="d"
        ).upper()

        if choice == "A":
            if risk == "HIGH":
                confirm = Prompt.ask(
                    "[bold red]⚠️  HIGH RISK operation. Type YES to confirm[/bold red]"
                )
                if confirm.strip() != "YES":
                    console.print("[yellow]  Confirmation failed. Returning to choices.[/yellow]")
                    continue

            console.print("[green]  ✅ Approved. Proceeding to execution...[/green]")
            return {
                **state,
                "hitl_decision": "approved",
            }

        elif choice == "D":
            console.print("[red]  ❌ Denied. Aborting. No command was executed.[/red]")
            return {
                **state,
                "hitl_decision": "denied",
            }

        elif choice == "E":
            console.print(
                f"[dim]  Current command: {state.get('generated_cmd', '')}[/dim]"
            )
            edited = Prompt.ask("[bold]  Enter your edited command[/bold]").strip()
            if not edited:
                console.print("[yellow]  No input received. Returning to choices.[/yellow]")
                continue

            console.print(
                f"[green]  ✏️  Command updated. Re-assessing risk and explanation...[/green]"
            )
            return {
                **state,
                "hitl_decision": "edit",
                "generated_cmd": edited,          
                "edited_cmd": edited,             
            }

        elif choice == "R":
            if retry_count >= MAX_RETRIES:
                console.print(
                    f"[red]  Maximum retries ({MAX_RETRIES}) reached. Aborting.[/red]"
                )
                return {
                    **state,
                    "hitl_decision": "denied",
                }

            console.print(
                f"[yellow]  🔁 Re-generating... (attempt {retry_count + 1}/{MAX_RETRIES})[/yellow]"
            )
            return {
                **state,
                "hitl_decision": "retry",
                "retry_count": retry_count + 1,
                "generated_cmd": None,
                "risk_level": None,
                "explanation": None,
            }