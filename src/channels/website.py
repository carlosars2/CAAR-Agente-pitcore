"""Website chat channel adapter (REST + WebSocket)."""

import logging

from src.channels.base import BaseChannel

logger = logging.getLogger(__name__)


class WebsiteChannel(BaseChannel):
    """Adapter for the website chat widget.

    Messages arrive via REST POST or WebSocket from the embedded widget.
    Responses are returned directly in the HTTP response or pushed via WebSocket.
    """

    async def receive_message(self, raw_payload: dict) -> tuple[str, str]:
        """Parse a website chat message.

        Expected payload: {"conversation_id": "...", "message": "..."}
        """
        conversation_id = raw_payload.get("conversation_id", "")
        message = raw_payload.get("message", "")
        return conversation_id, message

    async def send_message(self, conversation_id: str, text: str) -> None:
        """Website responses are returned inline — this is a no-op.

        For WebSocket connections, the message is pushed directly via the
        WebSocket handler in the routes layer.
        """
        logger.debug("Website response for %s: %s", conversation_id, text[:100])
