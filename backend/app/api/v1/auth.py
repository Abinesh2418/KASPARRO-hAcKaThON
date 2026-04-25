import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

DB_PATH = Path(__file__).parent.parent.parent.parent / "db" / "users.json"


class LoginRequest(BaseModel):
    username: str
    password: str


def _load_users() -> list[dict]:
    try:
        return json.loads(DB_PATH.read_text())
    except Exception:
        return []


@router.post("/auth/login")
def login(req: LoginRequest):
    users = _load_users()
    for user in users:
        if user["username"] == req.username and user["password"] == req.password:
            print(f"[AUTH] Login success: {req.username}")
            return {"username": user["username"], "name": user["name"]}
    print(f"[AUTH] Login failed: {req.username}")
    raise HTTPException(status_code=401, detail="Invalid username or password")
