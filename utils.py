from __future__ import annotations

from datetime import datetime
from typing import Any


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def safe_input(prompt: str) -> str:
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print("\nInput cancelled.")
        return ""


def press_enter() -> None:
    input("\nPress Enter to continue...")


def normalize_choice(value: str) -> str:
    return value.strip().lower()


def clamp_priority(p: str) -> str:
    p = normalize_choice(p)
    if p in ("low", "l"):
        return "low"
    if p in ("medium", "m", "med"):
        return "medium"
    if p in ("high", "h"):
        return "high"
    return ""


def clamp_status(s: str) -> str:
    s = normalize_choice(s)
    mapping = {
        "open": "open",
        "o": "open",
        "in_progress": "in_progress",
        "in progress": "in_progress",
        "ip": "in_progress",
        "blocked": "blocked",
        "b": "blocked",
        "resolved": "resolved",
        "r": "resolved",
        "done": "resolved",
    }
    return mapping.get(s, "")


def days_since_iso(iso_ts: str) -> int:
    """Return full days since an ISO timestamp; safe fallback to 0 if parse fails."""
    try:
        dt = datetime.fromisoformat(iso_ts)
        delta = datetime.now() - dt
        return max(0, int(delta.total_seconds() // 86400))
    except Exception:
        return 0


def short(text: str, n: int = 80) -> str:
    text = (text or "").strip()
    return text if len(text) <= n else text[: n - 3] + "..."
