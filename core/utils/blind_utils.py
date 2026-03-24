import hashlib
def hash_message(message: int) -> int:
    """
    Temporary hash function (to be replaced later).
    Converts message into SHA-256 hash (integer form).
    """
    message_bytes = str(message).encode()
    hash_hex = hashlib.sha256(message_bytes).hexdigest()
    return int(hash_hex, 16)
