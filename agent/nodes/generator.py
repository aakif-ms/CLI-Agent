import json
from langchain_core.messages import SystemMessage, HumanMessage
from rich.console import Console
from ..state import AgentState
from ..llm import get_llm

console = Console()

llm = get_llm()

SYSTEM_PROMPT = """You are an expert PowerShell engineer.

Convert the user's natural language request into a single, correct PowerShell command.

Respond with EXACTLY this JSON (no markdown, no extra text):
{
  "command": "The PowerShell command here",
  "intent": "One sentence: what this command does in plain English"
}

Rules:
- Output ONLY the JSON object. No explanations outside it.
- Write the best, most idiomatic PowerShell command for the task.
- Prefer single-line commands. Use semicolons or pipelines as needed.
- Use built-in cmdlets over external tools where possible.
- Do NOT include dangerous flags like -Force or -Recurse unless absolutely necessary.
- For file listing operations (ls, list, dir, etc.), use the current directory (.) unless a specific path is mentioned.
- Use $env:USERPROFILE only when the user explicitly asks for their home directory.
- If the request is ambiguous, make safe assumptions and note them in "intent".
"""

def generate_command(state: AgentState) -> AgentState:
    console.print("\n[bold cyan]⚙️  [Node 2 / Generator][/bold cyan] Generating command...")
    
    user_input = state["user_input"]
    if state.get("edited_cmd"):
        user_input = f"{user_input}\n\nNote: The user edited the previous attempt. Use this as the command: {state['edited_cmd']}"

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f'Task: "{user_input}"'),
    ]
    
    response = llm.invoke(messages)
    raw = response.content.strip()
    
    try:
        clean = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(clean)
        command = result.get("command", "").strip()
        intent = result.get("intent", "").strip()
    except (json.JSONDecodeError, KeyError):
        command = raw.strip()
        intent = "Command generated (could not parse intent)."

    console.print(f"  [yellow]📝 Command:[/yellow] [bold]{command}[/bold]")
    console.print(f"  [dim]Intent:  {intent}[/dim]")
    
    return {
        **state,
        "generated_command": command,
        "cmd_intent": intent,
        "edited_cmd": None, 
    }