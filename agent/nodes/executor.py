import os
import shutil
import subprocess
from rich.console import Console
from rich.panel import Panel
from ..state import AgentState

console = Console()

def _find_powershell() -> str:
    configured = os.getenv("POWERSHELL_PATH", "")
    if configured and shutil.which(configured):
        return configured
    if shutil.which("pwsh"):
        return "pwsh"
    if shutil.which("powershell"):
        return "powershell"
    
    return ""

def execute_command(state: AgentState) -> AgentState:
    console.print("\n[bold cyan]🚀 [Node 6 / Executor][/bold cyan] Executing command...")

    cmd = state.get("generated_command", "")
    
    ps_exe = _find_powershell()
    if not ps_exe:
        error_msg = (
            "PowerShell not found on this system.\n"
            "Install PowerShell Core: https://aka.ms/powershell\n"
            "Or set POWERSHELL_PATH in your .env file."
        )
        console.print(f"[red]  ❌ {error_msg}[/red]")
        return {
            **state,
            "execution_success": False,
            "error_message": error_msg,
        }
    
    console.print(f"  [dim]Using: {ps_exe}[/dim]")
    console.print(f"  [dim]Runnig: {cmd}[/dim]\n")

    try:
        result = subprocess.run(
            [ps_exe, "-NoProfile", "-NonInteractive", "-Command", cmd],
            capture_output=True,
            text=True,
            timeout=60
        ) 
        
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        success = result.returncode == 0

        if success:
            output = stdout or "(Command ran successfully with no output)"
            console.print(
                Panel(
                    f"[green]{output}[/green]",
                    title="[bold green]✅ Execution Successful[/bold green]",
                    border_style="green"
                )
            )
            return {
                **state,
                "execution_output": output,
                "execution_success": True,
                "error_message": None 
            }
        else:
            error = stderr or stdout or "Unknown error"
            console.print(f"[red]  ❌ Command failed (exit code {result.returncode})[/red]")
            return {
                **state,
                "execution_output": stdout,
                "execution_success": False,
                "error_message": error
            }
    except subprocess.TimeoutExpired:
        msg = "Command timed out after 60 seconds."
        console.print(f"[red]  ❌ {msg}[/red]")
        return {
            **state,
            "execution_success": False,
            "error_message": msg,
        }
    except Exception as exc:
        msg = f"Unexpected execution error: {exc}"
        console.print(f"[red]  ❌ {msg}[/red]")
        return {
            **state,
            "execution_success": False,
            "error_message": msg,
        }
