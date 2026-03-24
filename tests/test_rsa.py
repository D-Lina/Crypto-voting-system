# test_rsa_module.py
import pytest
from rsa_module import (
    extended_gcd, mod_inverse, is_prime,
    generate_keys, encrypt, decrypt, sign, verify
)


# Test fonctions utilitaires

def test_is_prime():
    assert is_prime(2) is True
    assert is_prime(3) is True
    assert is_prime(17) is True
    assert is_prime(18) is False
    assert is_prime(1) is False

def test_extended_gcd():
    g, x, y = extended_gcd(30, 20)
    assert g == 10
    assert 30*x + 20*y == g

def test_mod_inverse():
    assert mod_inverse(3, 11) == 4
    assert mod_inverse(7, 26) == 15
    with pytest.raises(ValueError):
        mod_inverse(2, 4)  # pas d’inverse


# Test génération de clés

def test_generate_keys_basic():
    keys = generate_keys(61, 53)
    pub = keys["public"]
    priv = keys["private"]
    n = keys["n"]
    phi = keys["phi"]

    # Clés correctes
    assert pub[1] == n
    assert priv[1] == n
    # Vérifier que e*d ≡ 1 mod phi
    e, _ = pub
    d, _ = priv
    assert (e*d) % phi == 1

def test_generate_keys_invalid():
    # p ou q non premiers
    with pytest.raises(ValueError):
        generate_keys(4, 5)
    with pytest.raises(ValueError):
        generate_keys(7, 7)
    # e non copremier avec phi
    with pytest.raises(ValueError):
        generate_keys(11, 13, e=12)


# Test encryption / decryption

def test_encrypt_decrypt():
    keys = generate_keys(61, 53)
    pub = keys["public"]
    priv = keys["private"]

    message = 42
    cipher = encrypt(message, pub)
    plain = decrypt(cipher, priv)
    assert plain == message

    # Message hors intervalle
    with pytest.raises(ValueError):
        encrypt(pub[1], pub)  # message == n

    with pytest.raises(ValueError):
        sign(pub[1], priv)  # message == n


# Test signature / verification

def test_sign_verify():
    keys = generate_keys(61, 53)
    pub = keys["public"]
    priv = keys["private"]

    message = 99
    signature = sign(message, priv)
    assert verify(message, signature, pub) is True
    # Mauvais message
    assert verify(message+1, signature, pub) is False
