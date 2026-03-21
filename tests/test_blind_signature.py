from blind_signature import blind_message, blind_sign, unblind_signature
# Fake RSA keys (for testing)
public_key = (17, 3233)
private_key = (2753, 3233)
def verify(signature, message, public_key):
    e, n = public_key
    return pow(signature, e, n) == message
def test_blind_signature():
    message = 7  # vote example
    print("Original message:", message)
    # Step 1: blind
    blinded, r = blind_message(message, public_key)
    # Step 2: sign
    signed_blind = blind_sign(blinded, private_key)
    # Step 3: unblind
    signature = unblind_signature(signed_blind, r, public_key)
    # Step 4: verify
    if verify(signature, message, public_key):
        print("\n✅ SUCCESS: Blind signature works!")
    else:
        print("\n❌ ERROR: Something is wrong")
if __name__ == "__main__":
    test_blind_signature()
