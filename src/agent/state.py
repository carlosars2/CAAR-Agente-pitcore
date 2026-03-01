"""LangGraph conversation state definition."""

from typing import Annotated

from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class ConversationState(TypedDict):
    """State that flows through the LangGraph graph."""

    # Core conversation
    messages: Annotated[list, add_messages]
    conversation_id: str
    channel: str  # "website" or "whatsapp"

    # Qualification data (populated as conversation progresses)
    lead_name: str
    lead_phone: str
    lead_email: str
    company_name: str
    specialty: str
    employees: str
    monthly_orders: str
    main_pain: str
    current_systems: str

    # Recommendation
    recommended_product: str  # "agent_overlay" or "build"
    recommended_package: str  # "starter", "pro", "enterprise"

    # Flow control
    conversation_phase: str  # "greeting", "qualification", "recommendation", "detail", "objection", "next_steps"
    should_escalate: bool
    escalation_reason: str
