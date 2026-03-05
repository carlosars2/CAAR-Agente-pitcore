"""
Test script — conversa com o CAAR direto no terminal.
Nao precisa de Redis, Docker ou FastAPI rodando.

Uso:
    pip install langchain langchain-anthropic langgraph
    export ANTHROPIC_API_KEY=sk-ant-...
    python test_chat.py
"""

import asyncio
import os

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_anthropic import ChatAnthropic

from src.agent.prompts.knowledge_base import get_knowledge_base_text
from src.agent.prompts.system_prompt import get_system_prompt
from src.agent.tools import ALL_TOOLS


async def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("ERRO: defina ANTHROPIC_API_KEY")
        print("  export ANTHROPIC_API_KEY=sk-ant-...")
        return

    llm = ChatAnthropic(
        model="claude-sonnet-4-6",
        temperature=0.3,
        api_key=api_key,
        max_tokens=1024,
    ).bind_tools(ALL_TOOLS)

    system = SystemMessage(content=get_system_prompt() + "\n\n" + get_knowledge_base_text())
    messages = [system]

    print("=" * 50)
    print("  CAAR — Pitcore & Systems (Claude)")
    print("  Digite sua mensagem (ou 'sair' para encerrar)")
    print("=" * 50)
    print()

    while True:
        user_input = input("Voce: ").strip()
        if not user_input or user_input.lower() in ("sair", "exit", "quit"):
            print("\nAte logo!")
            break

        messages.append(HumanMessage(content=user_input))

        # Agent loop (may call tools multiple times)
        for _ in range(5):  # max 5 tool rounds
            response = await llm.ainvoke(messages)
            messages.append(response)

            if not response.tool_calls:
                break

            # Execute tools and feed results back
            for tc in response.tool_calls:
                tool_fn = next((t for t in ALL_TOOLS if t.name == tc["name"]), None)
                if tool_fn:
                    try:
                        # Inject conversation_id for tools that need it
                        args = tc["args"]
                        if "conversation_id" in args:
                            args["conversation_id"] = "test-session"
                        result = tool_fn.invoke(args)
                        if asyncio.iscoroutine(result):
                            result = await result
                    except Exception as e:
                        result = f"Erro na tool: {e}"
                else:
                    result = f"Tool {tc['name']} nao encontrada"

                from langchain_core.messages import ToolMessage
                messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))

        # Print the final response
        if response.content:
            print(f"\nCAAR: {response.content}\n")
        else:
            print("\nCAAR: [sem resposta textual]\n")


if __name__ == "__main__":
    asyncio.run(main())
