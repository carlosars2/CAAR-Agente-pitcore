"""LangGraph node functions for the CAAR agent."""

import logging

from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode

from src.agent.prompts.knowledge_base import get_knowledge_base_text
from src.agent.prompts.system_prompt import get_system_prompt
from src.agent.tools import ALL_TOOLS
from src.memory.redis_memory import memory

logger = logging.getLogger(__name__)


# Tool execution node
tool_node = ToolNode(ALL_TOOLS)


def build_system_message() -> SystemMessage:
    """Build the full system message with prompt + knowledge base."""
    full_prompt = (
        get_system_prompt()
        + "\n\n"
        + get_knowledge_base_text()
    )
    return SystemMessage(content=full_prompt)


async def agent_node(state: dict, model) -> dict:
    """Main agent node that processes user messages and generates responses.

    This node:
    1. Ensures the system prompt is in the messages
    2. Calls the LLM with tools bound
    3. Returns the updated messages
    """
    messages = state["messages"]

    # Ensure system message is first
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [build_system_message()] + messages

    # Call the model with tools
    response = await model.ainvoke(messages)

    return {"messages": [response]}


async def save_messages_node(state: dict) -> dict:
    """Persist the latest exchange to Redis memory."""
    conversation_id = state.get("conversation_id", "")
    if not conversation_id:
        return state

    messages = state["messages"]
    # Save the last user and assistant messages
    for msg in messages[-2:]:
        role = getattr(msg, "type", "unknown")
        if role in ("human", "user"):
            await memory.append_message(conversation_id, "user", msg.content)
        elif role in ("ai", "assistant") and msg.content:
            await memory.append_message(conversation_id, "assistant", msg.content)

    return state


def should_use_tools(state: dict) -> str:
    """Router: decide whether to call tools or respond directly."""
    messages = state["messages"]
    last = messages[-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return "respond"
