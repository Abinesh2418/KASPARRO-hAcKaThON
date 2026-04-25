import json
import logging
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.schemas.chat import ChatRequest
from app.services import orchestrator_service, preference_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Stream an AI shopping assistant response as Server-Sent Events.

    Pipeline: Intent → Search → Compare → Explain → Final Response (streamed)
    Event types: session_id | token | metadata | done | error
    """
    session_id = preference_service.get_or_create_session(request.session_id)
    preference_service.append_message(session_id, "user", request.prompt)

    history = preference_service.get_messages(session_id)
    messages = [{"role": m["role"], "content": m["content"]} for m in history[-10:]]
    preferences = preference_service.get_preferences(session_id)

    async def event_stream():
        yield f"data: {json.dumps({'type': 'session_id', 'session_id': session_id})}\n\n"

        full_response = ""
        had_error = False

        async for event in orchestrator_service.run_pipeline(messages, preferences, session_id):
            yield f"data: {json.dumps(event)}\n\n"
            if event["type"] == "token":
                full_response += event["content"]
            elif event["type"] == "error":
                had_error = True
                break

        if not had_error and full_response:
            preference_service.append_message(session_id, "assistant", full_response)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
