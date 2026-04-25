import re
import uuid
from typing import Dict, Any, List

# In-memory session store — swap for PostgreSQL when ready
_sessions: Dict[str, Dict[str, Any]] = {}

STYLE_KEYWORDS = [
    "casual", "formal", "streetwear", "minimal", "minimalist", "bohemian",
    "athletic", "sporty", "romantic", "edgy", "classic", "preppy", "vintage",
    "chic", "elegant", "sophisticated", "bold", "feminine", "androgynous",
]
COLOR_KEYWORDS = [
    "black", "white", "navy", "blue", "red", "green", "yellow", "pink",
    "purple", "brown", "grey", "gray", "beige", "cream", "tan", "camel",
    "burgundy", "terracotta", "olive", "sage", "gold", "silver",
]
OCCASION_KEYWORDS = [
    "work", "office", "casual", "date", "date night", "party", "wedding",
    "beach", "gym", "travel", "weekend", "brunch", "cocktail", "formal",
]

_DEFAULT_PREFERENCES: Dict[str, Any] = {
    "style": [],
    "colors": [],
    "sizes": [],
    "budget_max": None,
    "budget_min": None,
    "occasions": [],
}


def get_or_create_session(session_id: str | None) -> str:
    sid = session_id or str(uuid.uuid4())
    if sid not in _sessions:
        _sessions[sid] = {
            "messages": [],
            "preferences": {**_DEFAULT_PREFERENCES},
        }
        print(f"[PREFERENCE] New session created: {sid}")
    else:
        print(f"[PREFERENCE] Existing session found: {sid} | {len(_sessions[sid]['messages'])} messages")
    return sid


def get_session(session_id: str) -> Dict[str, Any]:
    return _sessions.get(session_id, {})


def append_message(session_id: str, role: str, content: str) -> None:
    if session_id in _sessions:
        _sessions[session_id]["messages"].append({"role": role, "content": content})


def extract_and_merge_preferences(session_id: str, text: str) -> Dict[str, Any]:
    text_lower = text.lower()
    prefs = _sessions[session_id]["preferences"]

    new_styles = [s for s in STYLE_KEYWORDS if s in text_lower]
    new_colors = [c for c in COLOR_KEYWORDS if c in text_lower]
    new_occasions = [o for o in OCCASION_KEYWORDS if o in text_lower]

    size_matches = re.findall(r"\b(xs|s\b|m\b|l\b|xl|xxl|size\s+\d+|\d{2})\b", text_lower)
    new_sizes = list({m.strip() for m in size_matches})

    budget_match = re.search(
        r"(?:under|below|less than|max|budget[:\s]+)\s*[\$£€]?\s*(\d+)", text_lower
    )
    if budget_match:
        prefs["budget_max"] = int(budget_match.group(1))
        print(f"[PREFERENCE] Budget detected: {prefs['budget_max']}")

    prefs["style"] = _merge_unique(prefs["style"], new_styles)
    prefs["colors"] = _merge_unique(prefs["colors"], new_colors)
    prefs["occasions"] = _merge_unique(prefs["occasions"], new_occasions)
    prefs["sizes"] = _merge_unique(prefs["sizes"], new_sizes)

    print(f"[PREFERENCE] Extracted -> styles: {new_styles} | colors: {new_colors} | occasions: {new_occasions} | sizes: {new_sizes}")
    return prefs


def get_preferences(session_id: str) -> Dict[str, Any]:
    return _sessions.get(session_id, {}).get("preferences", {})


def get_messages(session_id: str) -> List[Dict[str, str]]:
    return _sessions.get(session_id, {}).get("messages", [])


def set_last_products(session_id: str, products: list) -> None:
    if session_id in _sessions:
        _sessions[session_id]["last_products"] = products
        print(f"[PREFERENCE] Stored {len(products)} last recommended products for session {session_id}")


def get_last_products(session_id: str) -> list:
    return _sessions.get(session_id, {}).get("last_products", [])


def _merge_unique(existing: List[str], new: List[str]) -> List[str]:
    combined = existing + [n for n in new if n not in existing]
    return combined[:10]
