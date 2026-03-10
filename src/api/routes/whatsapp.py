"""WhatsApp webhook routes for UAZAPI integration."""

import asyncio
import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from src.agent.graph import process_message
from src.channels.whatsapp import WhatsAppChannel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])

whatsapp_channel = WhatsAppChannel()


@router.post("/webhook")
async def uazapi_webhook(request: Request):
    """Receive webhook events from UAZAPI.

    UAZAPI posts message events to this endpoint.
    Returns 200 immediately and processes asynchronously to avoid timeouts.
    """
    try:
        payload = await request.json()
    except Exception:
        return JSONResponse({"status": "invalid json"}, status_code=400)

    logger.info("Webhook received: %s", payload)

    # Filter by event type — only process messages
    event_type = (
        payload.get("EventType", "")
        or payload.get("event", "")
        or payload.get("type", "")
    )
    if event_type not in ("messages", "message", "Message"):
        logger.info("Ignoring event type: %s", event_type)
        return {"status": "ignored", "event": event_type}

    # Ignore messages sent by us
    msg = payload.get("message", {})
    from_me = msg.get("fromMe", False) or msg.get("key", {}).get("fromMe", False)
    if from_me:
        return {"status": "ignored", "reason": "self_message"}

    # Ignore group messages
    if msg.get("isGroup", False):
        return {"status": "ignored", "reason": "group_message"}

    # Only process text messages
    msg_type = msg.get("type", "")
    if msg_type and msg_type != "text":
        return {"status": "ignored", "reason": f"unsupported_type:{msg_type}"}

    # Return 200 immediately, process in background
    asyncio.create_task(_process_webhook(payload))
    return JSONResponse({"status": "received"}, status_code=200)


async def _process_webhook(payload: dict):
    """Process webhook message asynchronously."""
    try:
        conversation_id, user_message = await whatsapp_channel.receive_message(payload)

        if not conversation_id or not user_message:
            logger.info("Empty message ignored")
            return

        logger.info("WhatsApp message from %s: %s", conversation_id, user_message[:50])

        response_text = await process_message(
            conversation_id=conversation_id,
            user_message=user_message,
            channel="whatsapp",
        )

        await whatsapp_channel.send_message(conversation_id, response_text)

    except Exception as e:
        logger.error("WhatsApp webhook processing error: %s", e, exc_info=True)
