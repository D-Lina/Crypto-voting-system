import pytest
from core.crypto.blind_signature import (
    blind_message,
    blind_sign,
    unblind_signature
)

# Fake RSA keys
public_key = (17, 3233)
private_key = (2753, 3233)

def verify(signature, message, public_key):
    e, n = public_key
    return pow(signature, e, n) == message

##test valide 
def test_blind_signature_valid():
    message = 7

    blinded, r = blind_message(message, public_key)
    signed_blind = blind_sign(blinded, private_key)
    signature = unblind_signature(signed_blind, r, public_key)

    assert verify(signature, message, public_key) is True

##test message invalide
def test_invalid_message():
    with pytest.raises(ValueError):
        blind_message(-5, public_key)

## Test mauvais r (blinding factor)

def test_invalid_unblind():
    message = 7

    blinded, r = blind_message(message, public_key)
    signed_blind = blind_sign(blinded, private_key)

    # r invalide volontairement
    with pytest.raises(ValueError):
        unblind_signature(signed_blind, 0, public_key)
