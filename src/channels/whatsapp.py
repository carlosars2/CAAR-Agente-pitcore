"""WhatsApp channel adapter via UAZAPI."""

import logging
import re

import httpx

from src.channels.base import BaseChannel
from src.config.settings import settings

logger = logging.getLogger(__name__)

MAX_MESSAGE_LENGTH = 4000


def markdown_to_whatsapp(text: str) -> str:
    """Convert Markdown formatting to WhatsApp formatting."""
    # Headers ## / ### → *bold*
    text = re.sub(r"^#{1,3}\s+(.+)$", r"*\1*", text, flags=re.MULTILINE)
    # **bold** → *bold* (WhatsApp bold)
    text = re.sub(r"\*\*(.+?)\*\*", r"*\1*", text)
    # Links [text](url) → text: url
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1: \2", text)
    # Remove horizontal lines
    text = re.sub(r"^-{3,}\s*$", "", text, flags=re.MULTILINE)
    # Clean excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _split_message(text: str) -> list[str]:
    """Split long messages to respect WhatsApp limit."""
    if len(text) <= MAX_MESSAGE_LENGTH:
        return [text]

    parts = []
    for paragraph in text.split("\n\n"):
        if parts and len(parts[-1]) + len(paragraph) + 2 <= MAX_MESSAGE_LENGTH:
            parts[-1] += "\n\n" + paragraph
        else:
            # If single paragraph exceeds limit, split by lines
            if len(paragraph) > MAX_MESSAGE_LENGTH:
                for line in paragraph.split("\n"):
                    if parts and len(parts[-1]) + len(line) + 1 <= MAX_MESSAGE_LENGTH:
                        parts[-1] += "\n" + line
                    else:
                        parts.append(line)
            else:
                parts.append(paragraph)
    return parts


class WhatsAppChannel(BaseChannel):
    """Adapter for WhatsApp via UAZAPI.

    UAZAPI sends webhooks when messages arrive.
    Responses are sent back via the UAZAPI REST endpoint.
    """

    async def receive_message(self, raw_payload: dict) -> tuple[str, str]:
        """Parse a UAZAPI webhook payload.

        UAZAPI webhook format:
        {
            "EventType": "messages",
            "chat": {"phone": "5511999999999"},
            "message": {
                "text": "message text",
                "fromMe": false,
                "isGroup": false,
                "type": "text"
            }
        }
        """
        chat = raw_payload.get("chat", {})
        msg = raw_payload.get("message", {})

        # Extract phone number from multiple possible fields
        phone = chat.get("phone", "") or msg.get("phone", "") or msg.get("from", "")
        if not phone:
            chatid = (
                msg.get("chatid", "")
                or msg.get("remoteJid", "")
                or msg.get("key", {}).get("remoteJid", "")
            )
            phone = chatid.split("@")[0] if chatid else ""
        phone = re.sub(r"[^\d]", "", phone)

        # Extract message text
        text = msg.get("text", "") or msg.get("content", "") or ""

        if not phone or not text:
            logger.warning("Invalid UAZAPI payload: no sender or text")

        return f"wa:{phone}", text

    async def send_message(self, conversation_id: str, text: str) -> None:
        """Send a text message via UAZAPI."""
        phone = conversation_id.replace("wa:", "")

        if not settings.uazapi_token:
            logger.warning("UAZAPI token not configured — message not sent")
            return

        # Convert markdown to WhatsApp formatting
        text = markdown_to_whatsapp(text)
        parts = _split_message(text)

        try:
            async with httpx.AsyncClient() as client:
                for part in parts:
                    response = await client.post(
                        f"{settings.uazapi_base_url}/send/text",
                        headers={
                            "token": settings.uazapi_token,
                            "Content-Type": "application/json",
                        },
                        json={
                            "number": phone,
                            "text": part,
                        },
                        timeout=15,
                    )
                    if response.status_code != 200:
                        logger.error(
                            "UAZAPI error %s: %s",
                            response.status_code,
                            response.text,
                        )
                    else:
                        logger.info("WhatsApp message sent to %s (%d chars)", phone, len(part))
        except Exception as e:
            logger.error("Failed to send WhatsApp message: %s", e)
            raise
