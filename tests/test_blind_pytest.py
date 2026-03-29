# test_blind_signature.py

import pytest
import core.crypto.blind_signature

# -----------------------------
# MOCK des dépendances
# -----------------------------
def fake_validate_vote(message):
    if message < 0 or message > 10:
        raise ValueError("Vote must be between 0 and 10")

def fake_log_action(action, data):
    pass

def fake_increment_total():
    pass

def fake_increment_rejected():
    pass

# Injecter les mocks
core.crypto.blind_signature.validate_vote = fake_validate_vote
core.crypto.blind_signature.log_action = fake_log_action
core.crypto.blind_signature.increment_total = fake_increment_total
core.crypto.blind_signature.increment_rejected = fake_increment_rejected


# -----------------------------
# Clés RSA test
# -----------------------------
PUBLIC_KEY = (5, 91)
PRIVATE_KEY = (29, 91)

def hash_func(m):
    return m % PUBLIC_KEY[1]


# -----------------------------
# TEST 1
# -----------------------------
def test_generate_blinding_factor():
    r = core.crypto.blind_signature.generate_blinding_factor(91)

    from math import gcd
    assert 2 <= r < 91
    assert gcd(r, 91) == 1


# -----------------------------
# TEST 2
# -----------------------------
def test_blind_signature_flow():
    message = 7

    blinded, r = core.crypto.blind_signature.blind_message(message, PUBLIC_KEY, hash_func)
    signed = core.crypto.blind_signature.blind_sign(blinded, PRIVATE_KEY)
    signature = core.crypto.blind_signature.unblind_signature(signed, r, PUBLIC_KEY)

    e, n = PUBLIC_KEY
    assert pow(signature, e, n) == hash_func(message)


# -----------------------------
# TEST 3
# -----------------------------
def test_invalid_message():
    with pytest.raises(ValueError):
        core.crypto.blind_signature.blind_message(-1, PUBLIC_KEY, hash_func)


# -----------------------------
# TEST 4
# -----------------------------
def test_invalid_unblind():
    message = 5

    blinded, r = core.crypto.blind_signature.blind_message(message, PUBLIC_KEY, hash_func)
    signed = core.crypto.blind_signature.blind_sign(blinded, PRIVATE_KEY)

    with pytest.raises(ValueError) :
        core.crypto.blind_signature.unblind_signature(signed, 0, PUBLIC_KEY)
