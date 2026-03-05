"""LangChain tools available to the CAAR agent."""

import json
import logging

import httpx
from langchain_core.tools import tool

from src.agent.prompts.knowledge_base import (
    AGENTS,
    BUILD_SOB_MEDIDA,
    DEMO_CONFIG,
)
from src.config.settings import settings
from src.memory.redis_memory import memory

logger = logging.getLogger(__name__)


@tool
async def capture_lead(
    conversation_id: str,
    name: str = "",
    phone: str = "",
    email: str = "",
    company_name: str = "",
    specialty: str = "",
    interest: str = "",
    main_pain: str = "",
) -> str:
    """Save lead contact information gathered during conversation.

    Use this tool whenever the customer shares their name, phone, email,
    company name, specialty, or expressed interest. You can call it multiple
    times as you gather more info — data is merged, not overwritten.

    Args:
        conversation_id: The current conversation ID.
        name: Customer's name.
        phone: Customer's phone number.
        email: Customer's email.
        company_name: Name of the automotive center.
        specialty: Type of automotive specialty.
        interest: What they're interested in (agent_overlay, build, cooperative, monetize).
        main_pain: Their main challenge or pain point.
    """
    lead_data = {
        k: v
        for k, v in {
            "name": name,
            "phone": phone,
            "email": email,
            "company_name": company_name,
            "specialty": specialty,
            "interest": interest,
            "main_pain": main_pain,
        }.items()
        if v
    }

    if not lead_data:
        return "Nenhuma informacao de lead fornecida."

    await memory.save_lead(conversation_id, lead_data)
    logger.info("Lead captured for %s: %s", conversation_id, list(lead_data.keys()))
    return f"Lead salvo com sucesso: {', '.join(lead_data.keys())}"


@tool
async def schedule_consultation(
    conversation_id: str,
    lead_name: str,
    lead_phone: str,
    preferred_date: str = "",
    preferred_time: str = "",
    notes: str = "",
) -> str:
    """Schedule a free consultation with a Pitcore specialist.

    Use this when the customer wants to talk to a human specialist.
    This notifies the team via WhatsApp.

    Args:
        conversation_id: The current conversation ID.
        lead_name: Customer's name.
        lead_phone: Customer's phone number.
        preferred_date: Preferred date for consultation.
        preferred_time: Preferred time for consultation.
        notes: Additional notes about what the customer wants to discuss.
    """
    if not settings.escalation_whatsapp:
        logger.warning("Escalation WhatsApp not configured")
        return "Consulta registrada. Nossa equipe entrara em contato em breve."

    message = (
        f"*Nova Consulta Agendada via CAAR*\n\n"
        f"Cliente: {lead_name}\n"
        f"Telefone: {lead_phone}\n"
    )
    if preferred_date:
        message += f"Data preferida: {preferred_date}\n"
    if preferred_time:
        message += f"Horario preferido: {preferred_time}\n"
    if notes:
        message += f"Observacoes: {notes}\n"
    message += f"\nConversa: {conversation_id}"

    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{settings.evolution_api_url}/message/sendText/{settings.evolution_instance}",
                headers={"apikey": settings.evolution_api_key},
                json={
                    "number": settings.escalation_whatsapp,
                    "text": message,
                },
                timeout=10,
            )
    except Exception as e:
        logger.error("Failed to notify team: %s", e)

    await memory.save_lead(conversation_id, {
        "consultation_requested": True,
        "preferred_date": preferred_date,
        "preferred_time": preferred_time,
    })

    return "Consulta agendada com sucesso! A equipe Pitcore entrara em contato para confirmar."


@tool
async def escalate_to_human(
    conversation_id: str,
    reason: str,
    customer_phone: str = "",
) -> str:
    """Transfer the conversation to a human consultant.

    Use this when:
    - Customer explicitly asks to talk to a person
    - Price negotiation or custom discount request
    - Legal or contractual questions
    - Customer is frustrated or unhappy
    - Issue is outside CAAR's scope

    Args:
        conversation_id: The current conversation ID.
        reason: Why the escalation is needed.
        customer_phone: Customer's phone for the human to contact.
    """
    if not settings.escalation_whatsapp:
        logger.warning("Escalation WhatsApp not configured")
        return "Transferencia solicitada. Um consultor entrara em contato em breve."

    message = (
        f"*Escalacao CAAR → Humano*\n\n"
        f"Motivo: {reason}\n"
        f"Conversa: {conversation_id}\n"
    )
    if customer_phone:
        message += f"Telefone do cliente: {customer_phone}\n"

    # Fetch conversation summary
    history = await memory.get_history(conversation_id)
    if history:
        last_msgs = history[-6:]  # Last 3 exchanges
        summary = "\n".join(
            f"{'Cliente' if m['role'] == 'user' else 'CAAR'}: {m['content'][:100]}"
            for m in last_msgs
        )
        message += f"\nUltimas mensagens:\n{summary}"

    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{settings.evolution_api_url}/message/sendText/{settings.evolution_instance}",
                headers={"apikey": settings.evolution_api_key},
                json={
                    "number": settings.escalation_whatsapp,
                    "text": message,
                },
                timeout=10,
            )
    except Exception as e:
        logger.error("Failed to escalate: %s", e)

    return "Conversa transferida para um consultor humano. Ele entrara em contato em breve."


@tool
def recommend_solution(
    employees: str = "",
    monthly_orders: str = "",
    main_pain: str = "",
    has_existing_system: bool = True,
    wants_complete_solution: bool = False,
) -> str:
    """Analyze the customer profile and recommend the best Pitcore solution line.

    Use this after gathering qualification data to decide between AI Agents or Build Sob Medida.
    NEVER mention packages, plans, or pricing — every solution is custom.

    Args:
        employees: Approximate number of employees.
        monthly_orders: Approximate monthly work orders.
        main_pain: The customer's main challenge.
        has_existing_system: Whether they already use some system/tool.
        wants_complete_solution: Whether they want to replace everything.
    """
    try:
        emp = int(employees) if employees else 0
    except ValueError:
        emp = 0
    try:
        orders = int(monthly_orders) if monthly_orders else 0
    except ValueError:
        orders = 0

    # Decision: Build Sob Medida
    if wants_complete_solution or not has_existing_system or emp > 30 or orders > 500:
        return (
            "RECOMENDACAO: Build Sob Medida\n"
            "Motivo: Perfil indica necessidade de sistema completo e integrado.\n"
            "Diferencial: 5 primeiras etapas GRATUITAS, demo de 7 dias sem compromisso.\n"
            "Proximo passo: Convidar para iniciar o diagnostico gratuito no portal ou agendar consulta.\n"
            "IMPORTANTE: Nao mencione precos ou pacotes. Valores definidos na consulta."
        )

    # Decision: AI Agents — suggest relevant agents based on pain
    pain_lower = main_pain.lower() if main_pain else ""
    suggested = []
    if any(w in pain_lower for w in ["atendimento", "whatsapp", "mensagem", "cliente", "agenda"]):
        suggested.append("Atendimento")
    if any(w in pain_lower for w in ["orcamento", "preco", "aprovacao", "demora"]):
        suggested.append("Orcamento")
    if any(w in pain_lower for w in ["cobranca", "inadimplencia", "pagamento", "devendo"]):
        suggested.append("Cobranca")
    if any(w in pain_lower for w in ["gestao", "numero", "kpi", "controle", "dado"]):
        suggested.append("Gestao")
    if any(w in pain_lower for w in ["estoque", "peca", "falta", "compra"]):
        suggested.append("Estoque")
    if any(w in pain_lower for w in ["margem", "lucro", "rentabilidade", "prejuizo"]):
        suggested.append("Margem")
    if any(w in pain_lower for w in ["garantia", "retrabalho", "qualidade", "retorno"]):
        suggested.append("Garantia")
    if not suggested:
        suggested = ["Atendimento", "Orcamento"]

    return (
        "RECOMENDACAO: Agentes de IA\n"
        f"Agentes sugeridos para a dor do cliente: {', '.join(suggested)}.\n"
        "Motivo: Resultado rapido, sem trocar sistema, conecta aos sistemas atuais.\n"
        "Diferencial: Demo gratuita de 7 dias, sem cartao.\n"
        "Proximo passo: Oferecer demo gratuita ou agendar consulta com especialista.\n"
        "IMPORTANTE: Nao mencione precos, pacotes ou planos. A combinacao ideal de agentes e definida na consulta."
    )


@tool
def get_agent_details(agent_id: str) -> str:
    """Get detailed information about a specific AI agent.

    Use this when the customer asks about a specific agent's capabilities.

    Args:
        agent_id: The agent identifier (atendimento, orcamento, cobranca, gestao, estoque, margem, garantia).
    """
    agent_id_lower = agent_id.lower().strip()
    for agent in AGENTS:
        if agent["id"] == agent_id_lower or agent_id_lower in agent["name"].lower():
            features = "\n".join(f"  - {f}" for f in agent["features"])
            return (
                f"**{agent['name']}**\n\n"
                f"{agent['description']}\n\n"
                f"Funcionalidades:\n{features}\n\n"
                f"Resultado esperado: {agent['result']}\n\n"
                f"Caso de uso tipico: {agent['use_case']}\n\n"
                f"Disponivel como parte da solucao personalizada — definida na consulta com especialista."
            )

    available = ", ".join(a["name"] for a in AGENTS)
    return f"Agente '{agent_id}' nao encontrado. Agentes disponiveis: {available}"


@tool
async def send_summary(
    conversation_id: str,
    phone: str = "",
    email: str = "",
) -> str:
    """Send a conversation summary to the customer via WhatsApp or email.

    Use this when the customer asks for a summary or when closing the conversation.

    Args:
        conversation_id: The current conversation ID.
        phone: Customer's WhatsApp number to send summary.
        email: Customer's email to send summary (future feature).
    """
    history = await memory.get_history(conversation_id)
    if not history:
        return "Nenhum historico encontrado para esta conversa."

    # Build summary from conversation
    summary_parts = ["*Resumo da Conversa — Pitcore & Systems*\n"]
    lead = await memory.get_lead(conversation_id)
    if lead:
        if lead.get("name"):
            summary_parts.append(f"Cliente: {lead['name']}")
        if lead.get("interest"):
            interest_map = {
                "agent_overlay": "Agentes de IA (Agent Overlay)",
                "build": "Build Sob Medida",
                "cooperative": "Modelo Cooperativo",
                "monetize": "Programa Monetize",
            }
            summary_parts.append(f"Interesse: {interest_map.get(lead['interest'], lead['interest'])}")
        if lead.get("recommended_package"):
            summary_parts.append(f"Pacote sugerido: {lead['recommended_package']}")

    summary_parts.append(f"\nTotal de mensagens: {len(history)}")
    summary_parts.append(f"\nPortal: https://pitcore.online")
    summary_parts.append("\nPara continuar, acesse nosso portal ou responda esta mensagem.")

    summary_text = "\n".join(summary_parts)

    if phone and settings.evolution_api_key:
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{settings.evolution_api_url}/message/sendText/{settings.evolution_instance}",
                    headers={"apikey": settings.evolution_api_key},
                    json={"number": phone, "text": summary_text},
                    timeout=10,
                )
            return f"Resumo enviado para {phone} via WhatsApp."
        except Exception as e:
            logger.error("Failed to send summary: %s", e)
            return "Nao foi possivel enviar o resumo no momento. Tente novamente mais tarde."

    return f"Resumo da conversa preparado:\n\n{summary_text}"


# List of all tools for the agent
ALL_TOOLS = [
    capture_lead,
    schedule_consultation,
    escalate_to_human,
    recommend_solution,
    get_agent_details,
    send_summary,
]
