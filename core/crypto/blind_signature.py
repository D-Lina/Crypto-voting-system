import random
from typing import Tuple

from core.utils.audit_log import log_action
from core.utils.counters import increment_total, increment_rejected
from core.utils.utils import validate_vote
# Generate blinding factor
def generate_blinding_factor(n: int) -> int:
    return random.randint(2, n - 1)
# Step 1: Blind message
def blind_message(message: int, public_key: Tuple[int, int]):
    validate_vote(message)
    increment_total()

    e, n = public_key
    r = generate_blinding_factor(n)

    blinded = (message * pow(r, e, n)) % n

    log_action("Message blinded", {
        "message": message,
        "blinded": blinded
    })

    return blinded, r
# Step 2: Sign blinded message
def blind_sign(blinded_message: int, private_key: Tuple[int, int]):
    d, n = private_key

    signed = pow(blinded_message, d, n)

    log_action("Blinded message signed", {
        "blinded": blinded_message,
        "signed": signed
    })

    return signed


# Step 3: Unblind signature
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
    if debug:
        log_step("Blind signature", blind_signature)
        log_step("Unblinded signature", signature)

    return signature
