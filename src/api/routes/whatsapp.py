"""WhatsApp webhook routes for Evolution API integration."""

import logging

from fastapi import APIRouter, Request

from src.agent.graph import process_message
from src.channels.whatsapp import WhatsAppChannel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])

whatsapp_channel = WhatsAppChannel()


@router.post("/webhook")
async def evolution_webhook(request: Request):
    """Receive webhook events from Evolution API.

    Evolution API posts message events to this endpoint.
    We process incoming messages through the CAAR agent and
    send the response back via the WhatsApp channel.
    """
    payload = await request.json()
    event = payload.get("event", "")

    # Only process incoming text messages
    if event not in ("messages.upsert",):
        return {"status": "ignored", "event": event}

    # Ignore messages sent by us (fromMe)
    data = payload.get("data", {})
    key = data.get("key", {})
    if key.get("fromMe", False):
        return {"status": "ignored", "reason": "self_message"}

    try:
        conversation_id, user_message = await whatsapp_channel.receive_message(payload)

        if not conversation_id or not user_message:
            return {"status": "ignored", "reason": "empty_message"}

        logger.info("WhatsApp message from %s: %s", conversation_id, user_message[:50])

        response_text = await process_message(
            conversation_id=conversation_id,
            user_message=user_message,
            channel="whatsapp",
        )

        await whatsapp_channel.send_message(conversation_id, response_text)

        return {"status": "ok", "conversation_id": conversation_id}

    except Exception as e:
        logger.error("WhatsApp webhook error: %s", e, exc_info=True)
        return {"status": "error", "detail": str(e)}
