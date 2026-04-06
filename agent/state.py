from typing import Literal, Optional
from typing_extensions import TypedDict

RiskLevel = Literal["LOW", "MEDIUM", "HIGH"]
NodeDecision = Literal["approved", "denied", "edit", "retry"]

class AgentState(TypedDict):
    user_input: str
    is_valid: Optional[bool]
    validation_reason: Optional[str]
    generated_command: str
    cmd_intent: str
    risk_level: RiskLevel
    risk_reason: Optional[str]
    explanation: str
    impact_summary: Optional[str]
    hitl_decision: NodeDecision
    edited_cmd: Optional[str]
    execution_output: Optional[str]
    execution_success: Optional[bool]
    error_message: Optional[str]
    error_explanation: Optional[str]
    suggested_fix: Optional[str]
    retry_count: int