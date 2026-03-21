import hashlib
import json
from typing import Optional
last_hash: Optional[str] = None
def log_action(action: str, data):
    global last_hash
    data_str = json.dumps(data, sort_keys=True)
    combined = (last_hash or "").encode() + data_str.encode()
    current_hash = hashlib.sha256(combined).hexdigest()
    last_hash = current_hash
    print(f"[AUDIT] {action} | hash: {current_hash}")
    return current_hash
