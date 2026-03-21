from core.crypto.blind_signature import (
    blind_message,
    blind_sign,
    unblind_signature
)
from core.utils.counters import get_stats, increment_rejected
# Fake RSA keys
public_key = (17, 3233)
private_key = (2753, 3233)
def verify(signature, message, public_key):
    e, n = public_key
    return pow(signature, e, n) == message
def test_blind_signature():
    message = 7  # valid vote
    print("Original message:", message)
    try:
        # Step 1
        blinded, r = blind_message(message, public_key)
        # Step 2
        signed_blind = blind_sign(blinded, private_key)
        # Step 3
        signature = unblind_signature(signed_blind, r, public_key)
        # Step 4
        if verify(signature, message, public_key):
            print("\n✅ SUCCESS: Blind signature works!")
        else:
            print("\n❌ ERROR: Verification failed")
    except ValueError as e:
        increment_rejected()
        print("\n❌ Rejected vote:", e)
    # Admin dashboard stats
    stats = get_stats()
    print("\n📊 Admin Stats:")
    print("Total votes:", stats["total_votes"])
    print("Rejected votes:", stats["rejected_votes"])
if __name__ == "__main__":
    test_blind_signature()
