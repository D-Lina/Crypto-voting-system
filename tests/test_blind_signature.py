from core.crypto.blind_signature import (
    blind_message,
    blind_sign,
    unblind_signature
)
from core.utils.blind_utils import hash_message
from core.utils.counters import get_stats

public_key = (17, 3233)
private_key = (2753, 3233)

def verify(signature, message, public_key, hash_func):
    e, n = public_key
    hashed = hash_func(message)
    return pow(signature, e, n) == hashed
def test_blind_signature():
    message = 7
    print("Original message:", message)

    try:
        # Step 1: blind
        blinded, r = blind_message(message, public_key, hash_message)
        # Step 2: sign
        signed_blind = blind_sign(blinded, private_key)
        # Step 3: unblind
        signature = unblind_signature(signed_blind, r, public_key)
        # Step 4: verify
        if verify(signature, message, public_key, hash_message):
            print("\n✅ SUCCESS: Blind signature works!")
        else:
            print("\n❌ ERROR: Verification failed")
    except ValueError as e:
        print("\n❌ Rejected vote:", e)
    # Admin stats
    stats = get_stats()
    print("\n📊 Admin Stats:")
    print("Total votes:", stats["total_votes"])
    print("Rejected votes:", stats["rejected_votes"])
if __name__ == "__main__":
    test_blind_signature()
