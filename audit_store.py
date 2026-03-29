import hashlib
import json
from typing import Optional

_trail: list[dict] = []
_last_hash: Optional[str] = None


def log_action(action: str, data: dict) -> str:
    global _last_hash
    data_str = json.dumps(data, sort_keys=True)
    combined = (_last_hash or "").encode() + data_str.encode()
    current_hash = hashlib.sha256(combined).hexdigest()
    _last_hash = current_hash
    _trail.append({"action": action, "hash": current_hash})
    return current_hash


def get_trail() -> list[dict]:
    return list(_trail)


def reset_trail() -> None:
    global _trail, _last_hash
    _trail = []
    _last_hash = None
