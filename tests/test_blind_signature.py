from blind_signature import blind_message, blind_sign, unblind_signature

# Fake RSA keys (for testing only)
public_key = (17, 3233)
private_key = (2753, 3233)


def verify(signature, message, public_key):
    e, n = public_key
    return pow(signature, e, n) == message


def test_blind_signature():
    message = 7  # vote example
    
    blinded, r = blind_message(message, public_key)
    signed_blind = blind_sign(blinded, private_key)
    signature = unblind_signature(signed_blind, r, public_key)
    
    if verify(signature, message, public_key):
        print("✅ Blind signature works!")
    else:
        print("❌ Error in blind signature")


if __name__ == "__main__":
    test_blind_signature()
