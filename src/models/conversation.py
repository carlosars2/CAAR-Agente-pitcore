"""Conversation-related data models."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Channel(str, Enum):
    WEBSITE = "website"
    WHATSAPP = "whatsapp"


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    conversation_id: str
    message: str
    channel: Channel = Channel.WEBSITE


class ChatResponse(BaseModel):
    conversation_id: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
