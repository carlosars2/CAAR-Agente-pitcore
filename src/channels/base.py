"""Abstract channel interface for messaging adapters."""

from abc import ABC, abstractmethod


class BaseChannel(ABC):
    """Interface that all messaging channel adapters must implement."""

    @abstractmethod
    async def receive_message(self, raw_payload: dict) -> tuple[str, str]:
        """Parse an incoming message from the channel.

        Args:
            raw_payload: The raw message data from the channel.

        Returns:
            Tuple of (conversation_id, message_text).
        """
        ...

    @abstractmethod
    async def send_message(self, conversation_id: str, text: str) -> None:
        """Send a response message back through the channel.

        Args:
            conversation_id: The conversation to reply to.
            text: The message text to send.
        """
        ...
