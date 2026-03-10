"""LangGraph state machine for the Pitcore agent."""

import logging
from functools import partial

from langchain_anthropic import ChatAnthropic
from langgraph.graph import END, StateGraph

from src.agent.nodes import (
    agent_node,
    build_system_message,
    save_messages_node,
    should_use_tools,
    tool_node,
)
from src.agent.state import ConversationState
from src.agent.tools import ALL_TOOLS
from src.config.settings import settings

logger = logging.getLogger(__name__)


def create_graph():
    """Build and compile the Pitcore agent graph.

    Graph flow:
        start → agent → (tools → agent)* → save → end

    The agent node calls the LLM, which may request tool calls.
    If tools are requested, execute them and loop back to the agent.
    Once the agent produces a final text response, save to memory and finish.
    """
    # Initialize LLM with tools
    llm = ChatAnthropic(
        model=settings.anthropic_model,
        temperature=settings.anthropic_temperature,
        api_key=settings.anthropic_api_key,
        max_tokens=1024,
    ).bind_tools(ALL_TOOLS)

    # Create the graph
    graph = StateGraph(ConversationState)

    # Add nodes
    graph.add_node("agent", partial(agent_node, model=llm))
    graph.add_node("tools", tool_node)
    graph.add_node("save", save_messages_node)

    # Set entry point
    graph.set_entry_point("agent")

    # Add conditional edges from agent
    graph.add_conditional_edges(
        "agent",
        should_use_tools,
        {
            "tools": "tools",
            "respond": "save",
        },
    )

    # Tools always go back to agent for another round
    graph.add_edge("tools", "agent")

    # Save always ends
    graph.add_edge("save", END)

    return graph.compile()


# Compiled graph singleton
pitcore_graph = create_graph()


async def process_message(
    conversation_id: str,
    user_message: str,
    channel: str = "website",
) -> str:
    """Process a user message through the Pitcore agent graph.

    Args:
        conversation_id: Unique conversation identifier.
        user_message: The user's message text.
        channel: "website" or "whatsapp".

    Returns:
        The agent's response text.
    """
    from langchain_core.messages import HumanMessage

    from src.memory.redis_memory import memory

    # Load conversation history from Redis
    history = await memory.get_history(conversation_id)

    # Build messages list
    messages = [build_system_message()]
    for msg in history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            from langchain_core.messages import AIMessage
            messages.append(AIMessage(content=msg["content"]))

    # Add current user message
    messages.append(HumanMessage(content=user_message))

    # Run the graph
    initial_state: ConversationState = {
        "messages": messages,
        "conversation_id": conversation_id,
        "channel": channel,
        "lead_name": "",
        "lead_phone": "",
        "lead_email": "",
        "company_name": "",
        "specialty": "",
        "employees": "",
        "monthly_orders": "",
        "main_pain": "",
        "current_systems": "",
        "recommended_product": "",
        "recommended_package": "",
        "conversation_phase": "greeting",
        "should_escalate": False,
        "escalation_reason": "",
    }

    result = await pitcore_graph.ainvoke(initial_state)

    # Extract the last AI message
    for msg in reversed(result["messages"]):
        if hasattr(msg, "type") and msg.type == "ai" and msg.content:
            return msg.content

    return "Desculpe, nao consegui processar sua mensagem. Tente novamente."
