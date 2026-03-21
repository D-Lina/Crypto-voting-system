import random
from typing import Tuple, Optional
# Optional Logger (for debugging)
def log_step(step: str, value):
    """
    Simple logger for debugging (can be disabled).
    """
    print(f"[{step}] -> {value}")
# Helper: Generate blinding factor
def generate_blinding_factor(n: int) -> int:
    """
    Generate a random blinding factor r such that 1 < r < n.
    """
    return random.randint(2, n - 1)
    
# Step 1: Blind the message
def blind_message(
    message: int,
    public_key: Tuple[int, int],
    debug: bool = False
) -> Tuple[int, int]:
    """
    Blind the message using RSA public key.

    Returns:
        blinded_message, r
    """
    if message <= 0:
        raise ValueError("Message must be a positive integer")

    e, n = public_key

    r = generate_blinding_factor(n)
    blinded = (message * pow(r, e, n)) % n

    if debug:
        log_step("Original message", message)
        log_step("Blinding factor (r)", r)
        log_step("Blinded message", blinded)

    return blinded, r
    
# Step 2: Sign blinded message
def blind_sign(
    blinded_message: int,
    private_key: Tuple[int, int],
    debug: bool = False
) -> int:
    """
    Administrator signs the blinded message.
    """
    d, n = private_key

    signed = pow(blinded_message, d, n)

    if debug:
        log_step("Blinded message received", blinded_message)
        log_step("Signed blinded message", signed)

    return signed
    
# Step 3: Unblind the signature
def unblind_signature(
    blind_signature: int,
    r: int,
    public_key: Tuple[int, int],
    debug: bool = False
) -> int:
    """
    Remove blinding factor to obtain valid signature.
    """
    _, n = public_key

    try:
        r_inv = pow(r, -1, n)  # modular inverse
    except ValueError:
        raise ValueError("Invalid blinding factor (no modular inverse)")

    signature = (blind_signature * r_inv) % n

    if debug:
        log_step("Blind signature", blind_signature)
        log_step("Unblinded signature", signature)

    return signature
