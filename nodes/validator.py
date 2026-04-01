from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from rich.console import Console
import json
from llm import get_llm
from state import AgentState

llm = get_llm()

console = Console()

SYSTEM_PROMPT = """You are a scope validator for a PowerShell CLI assistant.

Your ONLY job is to decide if the user's request is relevant to:
- PowerShell commands
- Windows/Linux system operations (files, folders, processes, services, networking, registry, etc.)
- Shell scripting tasks
- System administration

Respond with EXACTLY this JSON (no markdown, no extra text):
{
  "is_valid": true,
  "reason": "Brief explanation of why it is or isn't in scope"
}

Rules:
- is_valid = true  → request is a system/PowerShell task
- is_valid = false → request is off-topic (math, jokes, cooking, general knowledge, etc.)
"""

def validate_intent(state: AgentState) -> AgentState:
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f'User request: "{state["user_input"]}"'),
    ]
    
    response = llm.invoke(messages)
    raw = response.content.strip()
    try:
        clean = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(clean)
        is_valid = bool(result.get("is_valid", False))
        reason = result.get("reason", "No reason provided.")
    except (json.JSONDecodeError, KeyError):
        is_valid = any(
            kw in raw.lower()
            for kw in ["true", "powershell", "valid", "system", "file", "process"]
        )
        reason = raw[:200]
    
    if is_valid:
        console.print(
            f"  [green]✅ In scope[/green] — {reason}"
        )
    else:
        console.print(
            f"  [red]❌ Out of scope[/red] — {reason}"
        )

    return {
        **state,
        "is_valid": is_valid,
        "validation_reason": reason,
    }