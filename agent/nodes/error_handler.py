import json
from langchain_core.messages import HumanMessage, SystemMessage
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from ..state import AgentState
from ..llm import get_llm

console = Console()

SYSTEM_PROMPT = """You are a PowerShell debugger and expert.

A PowerShell command failed. Your job is to:
1. Explain the error in plain English (no jargon)
2. Suggest a corrected command that fixes the issue

Respond with EXACTLY this JSON (no markdown, no extra text):
{
  "error_explanation": "2-3 sentences: what went wrong and why, in plain English",
  "suggested_fix": "The corrected PowerShell command string"
}
"""

def handle_error(state: AgentState) -> AgentState:
    console.print("\n[bold cyan]🛠️  [Node 7 / Error Handler][/bold cyan] Analyzing failure...\n")
    
    error_msg = state.get("error_message", "Unknown Error")
    failed_cmd = state.get("generated_command", "N/A")
    original_intent = state.get("user_input", "")

    console.print(f"  [red]Error:[/red] [dim]{error_msg[:300]}[/dim]")

    llm = get_llm()
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=(
                f"Original Task: {original_intent}\n"
                f"Failed command: `{failed_cmd}`\n"
                f"Error output:\n{error_msg}"
            )
        ),
    ]  
    
    response = llm.invoke(messages)
    raw = response.content.strip()
    
    try:
        clean = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(clean)
        error_explanation = result.get("error_explanation", "Could not parse explanation.")
        suggested_fix = result.get("suggested_fix", "").strip()
    except (json.JSONDecodeError, KeyError):
        error_explanation = raw[:300]
        suggested_fix = ""

    console.print(
        Panel(
            f"[bold]What went wrong:[/bold]\n{error_explanation}\n\n"
            + (
                f"[bold]Suggested fix:[/bold]\n[yellow]{suggested_fix}[/yellow]"
                if suggested_fix
                else "[dim]No fix suggestion available.[/dim]"
            ),
            title="[bold red]🔴 Execution Failed[/bold red]",
            border_style="red",
            padding=(1, 2),
        )
    )
    
    if not suggested_fix:
        console.print("[dim]No retry available. Exiting.[/dim]")
        return{
            **state,
            "error_explanation": error_explanation,
            "suggested_fix": "",
            "hitl_decision": "denied"
        }
    
    console.print("\n[bold yellow]Would you like to retry with the suggested fix?[/bold yellow]")
    choice = Prompt.ask(
        "[dim][Y] Yes, retry   [N] No, abort[/dim]",
        choices=["Y", "N", "y", "n"],
        default="N",
    ).upper()
    
    if choice == "Y":
        console.print(
            f"[green]  ✅ Retrying with fix: [bold]{suggested_fix}[/bold][/green]"
        )
        return {
            **state,
            "error_explanation": error_explanation,
            "suggested_fix": suggested_fix,
            "generated_command": suggested_fix,
            "error_message": None,
            "execution_success": None,
            "hitl_decision": "approved"
        }
    else:
        console.print("[red]  ❌ Aborted. No command was re-executed.[/red]")
        return {
            **state,
            "error_explanation": error_explanation,
            "suggested_fix": suggested_fix,
            "hitl_decision": "denied",
        }
