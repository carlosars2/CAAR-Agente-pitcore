"""Chat routes — REST and WebSocket for the website widget."""

import json
import logging
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.agent.graph import process_message
from src.models.conversation import Channel, ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """REST endpoint: receive a message, process through Pitcore, return response."""
    conversation_id = request.conversation_id or str(uuid.uuid4())

    response_text = await process_message(
        conversation_id=conversation_id,
        user_message=request.message,
        channel=request.channel.value,
    )

    return ChatResponse(
        conversation_id=conversation_id,
        message=response_text,
    )


@router.websocket("/ws/{conversation_id}")
async def websocket_chat(websocket: WebSocket, conversation_id: str):
    """WebSocket endpoint for real-time chat from the website widget."""
    await websocket.accept()
    logger.info("WebSocket connected: %s", conversation_id)

    try:
        while True:
            data = await websocket.receive_text()

            try:
                payload = json.loads(data)
                user_message = payload.get("message", data)
            except json.JSONDecodeError:
                user_message = data

            if not user_message.strip():
                continue

            response_text = await process_message(
                conversation_id=conversation_id,
                user_message=user_message,
                channel="website",
            )

            await websocket.send_json({
                "conversation_id": conversation_id,
                "message": response_text,
            })

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected: %s", conversation_id)
    except Exception as e:
        logger.error("WebSocket error for %s: %s", conversation_id, e)
        try:
            await websocket.close()
        except Exception:
            pass
