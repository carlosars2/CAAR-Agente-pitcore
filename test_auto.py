"""Automated test — sends a few messages and prints the CAAR responses."""

import asyncio
import os
import sys

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_anthropic import ChatAnthropic

# Set key from .env manually for this test
from dotenv import load_dotenv
load_dotenv()

from src.agent.prompts.knowledge_base import get_knowledge_base_text
from src.agent.prompts.system_prompt import get_system_prompt
from src.agent.tools import ALL_TOOLS


TEST_MESSAGES = [
    "Ola, boa tarde!",
    "Tenho uma oficina mecanica com 12 funcionarios, fazemos umas 150 OS por mes",
    "Meu maior problema e que perco muita grana com inadimplencia e demoro pra fazer orcamento",
    "Quanto custa?",
    "E caro, preciso pensar...",
]


async def run_agent(messages, user_text):
    """Send a message and get response, handling tool calls."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    llm = ChatAnthropic(
        model="claude-sonnet-4-6",
        temperature=0.3,
        api_key=api_key,
        max_tokens=1024,
    ).bind_tools(ALL_TOOLS)

    messages.append(HumanMessage(content=user_text))

    for _ in range(5):
        response = await llm.ainvoke(messages)
        messages.append(response)

        if not response.tool_calls:
            break

        for tc in response.tool_calls:
            tool_fn = next((t for t in ALL_TOOLS if t.name == tc["name"]), None)
            if tool_fn:
                try:
                    args = tc["args"]
                    if "conversation_id" in args:
                        args["conversation_id"] = "test-auto"
                    result = tool_fn.invoke(args)
                    if asyncio.iscoroutine(result):
                        result = await result
                except Exception as e:
                    result = f"Erro: {e}"
            else:
                result = f"Tool {tc['name']} nao encontrada"
            messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))

    return response.content if response.content else "[sem resposta]"


async def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("ERRO: ANTHROPIC_API_KEY nao definida")
        return

    system = SystemMessage(content=get_system_prompt() + "\n\n" + get_knowledge_base_text())
    messages = [system]

    print("=" * 60)
    print("  TESTE AUTOMATICO — CAAR Agent (Claude)")
    print("=" * 60)

    for i, user_msg in enumerate(TEST_MESSAGES, 1):
        print(f"\n--- Mensagem {i}/{len(TEST_MESSAGES)} ---")
        print(f"VOCE: {user_msg}")

        try:
            response = await run_agent(messages, user_msg)
            print(f"\nCAAR: {response}")
        except Exception as e:
            print(f"\nERRO: {e}")
            break

    print("\n" + "=" * 60)
    print("  TESTE CONCLUIDO")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
