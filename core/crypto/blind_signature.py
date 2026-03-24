import random
from typing import Tuple, Callable

from core.utils.audit_log import log_action
from core.utils.counters import increment_total, increment_rejected
from core.utils.utils import validate_vote

def generate_blinding_factor(n: int) -> int:
    return random.randint(2, n - 1)
def blind_message(
    message: int,
    public_key: Tuple[int, int],
    hash_func: Callable[[int], int]
):
    try:
        validate_vote(message)
        increment_total()
    except ValueError:
        increment_rejected()
        raise
    e, n = public_key
    hashed = hash_func(message)
    r = generate_blinding_factor(n)
    blinded = (hashed * pow(r, e, n)) % n
    log_action("Message blinded", {
        "message": message,
        "hashed": hashed,
        "blinded": blinded
    })
    return blinded, r
def blind_sign(blinded_message: int, private_key: Tuple[int, int]):
    d, n = private_key
    signed = pow(blinded_message, d, n)
    log_action("Blinded message signed", {
        "blinded": blinded_message,
        "signed": signed
    })
    return signed
def unblind_signature(blind_signature: int, r: int, public_key: Tuple[int, int]):
    _, n = public_key
    try:
        r_inv = pow(r, -1, n)
    except ValueError:
        raise ValueError("Invalid blinding factor")
    signature = (blind_signature * r_inv) % n
    log_action("Signature unblinded", {
        "signature": signature
    })
    return signature
