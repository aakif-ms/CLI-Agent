import json
from langchain_core.messages import HumanMessage, SystemMessage
from rich.console import Console
from ..state import AgentState
from ..llm import get_llm

console = Console()

llm = get_llm()

RISK_EMOJI = {
    "LOW": "🟢",
    "MEDIUM": "🟡",
    "HIGH": "🔴",
}

SYSTEM_PROMPT = """You are a PowerShell security analyst specializing in command risk assessment.

Classify the provided PowerShell command into exactly ONE of these risk levels:
- LOW    → Read-only, non-destructive, easily reversible (e.g., Get-*, New-Item directory, Write-Output)
- MEDIUM → Modifies state but recoverable (e.g., Move-Item, Copy-Item, Start-Service, Stop-Process)
- HIGH   → Destructive, irreversible, or potentially dangerous (e.g., Remove-Item, Format-*, Stop-Service, Set-Registry, -Force -Recurse on deletions, rm -rf equivalents)

Respond with EXACTLY this JSON (no markdown, no extra text):
{
  "risk_level": "LOW" | "MEDIUM" | "HIGH",
  "reason": "One sentence explaining why this risk level was assigned"
}
"""

def assess_risk(state: AgentState) -> AgentState:
    console.print("\n[bold cyan]🛡️  [Node 3 / Risk Assessor][/bold cyan] Evaluating risk...")
    
    cmd = state.get("generated_command", "")
    llm = get_llm()

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f'PowerShell command: `{cmd}`'),
    ]
    
    response = llm.invoke(messages)
    raw = response.content.strip()
    
    try:
        clean = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(clean)
        risk_level = result.get("risk_level", "MEDIUM").upper()
        reason = result.get("reason", "No reason provided.")

        if risk_level not in ("LOW", "MEDIUM", "HIGH"):
            risk_level = "MEDIUM"
    except (json.JSONDecodeError, KeyError):
        risk_level = "MEDIUM"
        reason = "Could not pass risk assessment. Defaulting to MEDIUM"
    
    emoji = RISK_EMOJI.get(risk_level, "⚪")
    color_map = {"LOW": "green", "MEDIUM": "yellow", "HIGH": "red"}
    color = color_map.get(risk_level, "white")
    
    console.print(
        f"  [{color}]{emoji} Risk Level: {risk_level}[/{color}] — {reason}"
    )

    return {
        **state,
        "risk_level": risk_level,
        "risk_reason": reason,
    }