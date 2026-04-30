# 🧠 Agentic PowerShell CLI Assistant

A local CLI that converts natural-language requests into validated PowerShell commands using a LangGraph multi-node workflow with human approval before execution.

## 🎯 What This Project Does

This tool helps you run system tasks faster while keeping control in your hands.

- 💬 Accepts a natural-language request
- Validates whether the request is in PowerShell/system scope
- Generates an idiomatic PowerShell command
- 🚨 Classifies command risk as LOW, MEDIUM, or HIGH
- Explains command behavior and impact in plain language
- 👤 Requires HITL approval before execution
- Handles runtime failures with an LLM-assisted fix suggestion

## 📷 Demo Video

https://github.com/user-attachments/assets/958fe7ff-9426-422f-8518-20f3da26f35b

## ✨ Features

- Natural language to PowerShell command generation
- LangGraph-based multi-node orchestration
- Human-in-the-loop safety gate before execution
- Risk classification with explicit rationale
- Command explanation and expected impact preview
- Retry and command-edit options during approval
- Error analysis with optional auto-retry using suggested fix

## 🏗️ Architecture

The workflow is implemented as a stateful LangGraph pipeline:

1. validate_intent
2. generate_command
3. assess_risk
4. explain_command
5. hitl_approval
6. execute_command
7. handle_error (only on execution failure)

Routing behavior:

- Out-of-scope requests end immediately after validation
- Denied requests end immediately at HITL
- Edited commands go back through risk and explanation
- Re-generated commands return to command generation (up to retry limits)
- Execution failures go to error handling, then optional retry

## 🛠️ Tech Stack

- Python 3.12+
- Typer (CLI)
- Rich (terminal UX)
- LangGraph + LangChain
- OpenAI chat model via langchain-openai

## 📁 Project Structure

```text
agent/
	main.py            # Typer CLI entrypoint
	graph.py           # LangGraph definition and routing
	llm.py             # ChatOpenAI factory
	state.py           # Shared typed state
	nodes/
		validator.py     # Scope validation
		generator.py     # Command generation
		risk.py          # Risk classification
		explainer.py     # Human-readable explanation
		hitl.py          # Human approval/edit/retry
		executor.py      # PowerShell execution
		error_handler.py # Failure analysis + fix suggestion
```

## ⚙️ Prerequisites

- Windows, Linux, or macOS
- Python 3.12 or newer
- PowerShell available as `pwsh` or `powershell`
- OpenAI API key

## 📦 Installation

1. Clone the repository and move into the project directory.
2. Create and activate a virtual environment.
3. Install the package in editable mode.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

## ⚡ Configuration

Create a `.env` file in the repository root.

```env
OPENAI_API_KEY=your_openai_api_key_here
# Optional: override PowerShell executable path
# POWERSHELL_PATH=C:\Program Files\PowerShell\7\pwsh.exe
```

Notes:

- `OPENAI_API_KEY` is required for LLM nodes.
- `POWERSHELL_PATH` is optional and only needed if auto-detection fails.

## 🚀 Usage

Run the CLI via the installed script:

```powershell
agent "list all running processes"
```

Or via module invocation:

```powershell
python -m agent.main "show all services that are stopped"
```

## 👥 HITL Approval Options

When prompted, you can choose:

- `A` Approve and execute
- `D` Deny and abort
- `E` Edit the generated command, then re-assess risk
- `R` Re-generate command (limited retries)

For HIGH-risk commands, explicit confirmation (`YES`) is required before execution.

## 🔒 Safety Model

- Validation gate prevents off-topic requests from executing
- Risk assessor highlights dangerous or destructive operations
- Human approval is mandatory before execution
- Execution runs with `-NoProfile -NonInteractive`
- Subprocess timeout protects against long-running commands
- Error handler can suggest a safer corrected command

## 📋 Example Session

```text
Request: "delete all temp files in current folder"
-> Validator: in scope
-> Generator: produces PowerShell command
-> Risk: HIGH
-> Explainer: summarizes impact
-> HITL: requires approval and YES confirmation
-> Executor: runs only if approved
```

## 🐛 Troubleshooting

- PowerShell not found:
	- Install PowerShell Core (`pwsh`) or set `POWERSHELL_PATH` in `.env`.
- OpenAI authentication errors:
	- Verify `OPENAI_API_KEY` is set and valid.
- Command keeps failing:
	- Review the suggested fix in error handler and retry selectively.

## 💻 Development

Run directly during development:

```powershell
python -m agent.main "your request here"
```

Core files to start with:

- `agent/main.py`
- `agent/graph.py`
- `agent/state.py`
- `agent/nodes/*.py`
