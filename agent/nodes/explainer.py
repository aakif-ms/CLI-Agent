import json
from langchain_core.messages import HumanMessage, SystemMessage
from rich.console import Console
from rich.panel import Panel
from ..state import AgentState
from ..llm import get_llm

llm = get_llm()
console = Console()

SYSTEM_PROMPT = """You are a PowerShell educator. Your job is to clearly explain a PowerShell command
to a non-expert user who needs to approve or deny its execution.

Be clear, concise, and accurate. Avoid jargon. Use plain English.

Respond with EXACTLY this JSON (no markdown, no extra text):
{
  "explanation": "2-3 sentences explaining what the command does and how it works",
  "impact": "1 sentence: what will be different on the system after this runs"
}
"""

def explainer(state: AgentState) -> AgentState:
    console.print("\n[bold cyan]📖 [Node 4 / Explainer][/bold cyan] Generating explanation...")
    
    cmd = state.get("generated_command", "")
    risk = state.get("risk_level", "MEDIUM")
    intent = state.get("cmd_intent", "")
    
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=(
                f'Command: `{cmd}`\n'
                f'Intent: {intent}\n'
                f'Risk Level: {risk}'
            )
        ),
    ]    

    response = llm.invoke(messages)
    raw = response.content.strip()

    try:
        clean = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(clean)
        explanation = result.get("explanation", "No explanation available.")
        impact = result.get("impact", "No impact summary available.")
    except (json.JSONDecodeError, KeyError):
        explanation = raw[:300]
        impact = "Could not generate impact summary."
    
    risk_colors = {"LOW": "green", "MEDIUM": "yellow", "HIGH": "red"}
    color = risk_colors.get(risk, "white")

    console.print(
        Panel(
            f"[bold]What it does:[/bold]\n{explanation}\n\n"
            f"[bold]Impact:[/bold]\n{impact}",
            title="[bold blue]📋 Command Explanation[/bold blue]",
            border_style=color,
            padding=(1, 2),
        )
    )
    
    return {
        **state,
        "explanation": explanation,
        "impact_summary": impact,
    }
