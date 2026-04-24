from fastapi import APIRouter, HTTPException
from app.services import preference_service

router = APIRouter()


@router.get("/preferences/{session_id}")
async def get_preferences(session_id: str):
    prefs = preference_service.get_preferences(session_id)
    if not prefs:
        raise HTTPException(status_code=404, detail="Session not found.")
    return prefs
