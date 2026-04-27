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
    print(f"\n{'='*60}")
    print(f"[CHAT] New request received")
    print(f"[CHAT] Prompt: {request.prompt[:100]}{'...' if len(request.prompt) > 100 else ''}")
    print(f"[CHAT] Session ID (incoming): {request.session_id}")

    session_id = preference_service.get_or_create_session(request.session_id)
    print(f"[CHAT] Session resolved: {session_id}")

    preference_service.append_message(session_id, "user", request.prompt)

    history = preference_service.get_messages(session_id)
    messages = [{"role": m["role"], "content": m["content"]} for m in history[-10:]]
    preferences = preference_service.get_preferences(session_id)
    print(f"[CHAT] History length: {len(history)} messages | Preferences: {preferences}")

    async def event_stream():
        print(f"[CHAT] SSE stream started -> session_id event sent")
        yield f"data: {json.dumps({'type': 'session_id', 'session_id': session_id})}\n\n"

        full_response = ""
        had_error = False
        token_count = 0

        async for event in orchestrator_service.run_pipeline(messages, preferences, session_id, request.pre_searched_products):
            yield f"data: {json.dumps(event)}\n\n"
            if event["type"] == "token":
                full_response += event["content"]
                token_count += 1
            elif event["type"] == "metadata":
                products = event.get("products", [])
                print(f"[CHAT] Metadata event sent -> {len(products)} products, preferences: {event.get('preferences', {})}")
            elif event["type"] == "done":
                print(f"[CHAT] Done event sent | Total tokens streamed: {token_count}")
                print(f"[CHAT] Full response: {full_response[:200]}{'...' if len(full_response) > 200 else ''}")
            elif event["type"] == "error":
                print(f"[CHAT] ERROR event sent: {event.get('message')}")
                had_error = True
                break

        if not had_error and full_response:
            preference_service.append_message(session_id, "assistant", full_response)
            print(f"[CHAT] Assistant response saved to session")
        print(f"{'='*60}\n")

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
