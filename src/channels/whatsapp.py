"""WhatsApp channel adapter via Evolution API."""

import logging

import httpx

from src.channels.base import BaseChannel
from src.config.settings import settings

logger = logging.getLogger(__name__)


class WhatsAppChannel(BaseChannel):
    """Adapter for WhatsApp via Evolution API.

    Evolution API sends webhooks when messages arrive.
    Responses are sent back via the Evolution API REST endpoint.
    """

    async def receive_message(self, raw_payload: dict) -> tuple[str, str]:
        """Parse an Evolution API webhook payload.

        Evolution API webhook format:
        {
            "data": {
                "key": {"remoteJid": "5511999999999@s.whatsapp.net", ...},
                "message": {"conversation": "message text", ...},
                ...
            }
        }
        """
        data = raw_payload.get("data", {})
        key = data.get("key", {})
        message_data = data.get("message", {})

        # Extract sender phone (conversation_id = phone number)
        remote_jid = key.get("remoteJid", "")
        conversation_id = remote_jid.replace("@s.whatsapp.net", "").replace("@g.us", "")

        # Extract message text (Evolution API has multiple message types)
        text = (
            message_data.get("conversation")
            or message_data.get("extendedTextMessage", {}).get("text")
            or ""
        )

        if not conversation_id or not text:
            logger.warning("Invalid WhatsApp payload: no sender or text")

        return f"wa:{conversation_id}", text

    async def send_message(self, conversation_id: str, text: str) -> None:
        """Send a text message via Evolution API."""
        # Remove wa: prefix to get the phone number
        phone = conversation_id.replace("wa:", "")

        if not settings.evolution_api_key:
            logger.warning("Evolution API key not configured — message not sent")
            return

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.evolution_api_url}/message/sendText/{settings.evolution_instance}",
                    headers={"apikey": settings.evolution_api_key},
                    json={
                        "number": phone,
                        "text": text,
                    },
                    timeout=15,
                )
                response.raise_for_status()
                logger.info("WhatsApp message sent to %s", phone)
        except httpx.HTTPStatusError as e:
            logger.error("Evolution API error %s: %s", e.response.status_code, e.response.text)
            raise
        except Exception as e:
            logger.error("Failed to send WhatsApp message: %s", e)
            raise
