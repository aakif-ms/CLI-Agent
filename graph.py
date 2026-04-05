from langgraph.graph import StateGraph, END

from state import AgentState
from nodes.validator import validate_intent
from nodes.generator import generate_command
from nodes.risk import assess_risk
from nodes.explainer import explainer
from nodes.hitl import hitl_approval
from nodes.executor import execute_command
from nodes.error_handler import handle_error

def route_after_validation(state: AgentState) -> str:
    return "generate_command" if state.get("is_valid") else END

def route_after_hitl(state: AgentState) -> str:
    decision = state.get("hitl_decision")
    if decision == "approved":
        return "execute_command"
    elif decision == "denied":
        return END
    elif decision == "edit":
        return "assess_risk"
    elif decision == "retry":
        return "generate_command"
    return END

def route_after_execution(state: AgentState) -> str:
    if state.get("execution_sucess"):
        return END
    return "handle_error"

def route_after_error_handler(state: AgentState) -> str:
    decision = state.get("hitl_decision")
    if decision == "approved":
        return "execute_command"
    return END

def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("validate_intent", validate_intent)   
    graph.add_node("generate_command", generate_command) 
    graph.add_node("assess_risk", assess_risk)           
    graph.add_node("explain_command", explainer)   
    graph.add_node("hitl_approval", hitl_approval)       
    graph.add_node("execute_command", execute_command)   
    graph.add_node("handle_error", handle_error)         

    graph.set_entry_point("validate_intent")

    graph.add_conditional_edges(
        "validate_intent",
        route_after_validation,
        {
            "generate_command": "generate_command",
            END: END
        },
    )
    graph.add_edge("generate_command", "assess_risk")
    graph.add_edge("assess_risk", "explain_command")
    graph.add_edge("explain_command", "hitl_approval")
    graph.add_conditional_edges(
        "hitl_approval",
        route_after_hitl,
        {
            "execute_command": "execute_command",
            "assess_risk": "assess_risk",
            "generate_command": "generate_command",
            END: END
        },
    )
    graph.add_conditional_edges(
        "execute_command",
        route_after_execution,
        {
            "handle_error": "handle_error",
            END: END
        },
    )
    graph.add_conditional_edges(
        "handle_error",
        route_after_error_handler,
        {
            "execute_command": "execute_command",
            END: END,
        },
    )
    
    return graph.compile()