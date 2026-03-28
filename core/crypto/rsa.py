from math import gcd

# ── Math utilities ─────────────────────────

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    g, x1, y1 = extended_gcd(b % a, a)
    return g, y1 - (b // a) * x1, x1


def mod_inverse(a, modulus):
    g, x, _ = extended_gcd(a % modulus, modulus)
    if g != 1:
        raise ValueError("Inverse modulaire inexistant")
    return x % modulus


def is_prime(num):
    if num < 2:
        return False
    if num % 2 == 0 and num != 2:
        return False
    for i in range(3, int(num**0.5) + 1, 2):
        if num % i == 0:
            return False
    return True


# ── Key generation ─────────────────────────

def generate_keys(p, q, e=None):
    if not is_prime(p) or not is_prime(q):
        raise ValueError("p ou q non premier")
    if p == q:
        raise ValueError("p et q doivent être différents")

    n = p * q
    phi = (p - 1) * (q - 1)

    # choisir e
    if e is None:
        e = 3
        while gcd(e, phi) != 1:
            e += 2
    else:
        if gcd(e, phi) != 1:
            raise ValueError("e non copremier avec phi")

    d = mod_inverse(e, phi)

    return {
        "public": (e, n),
        "private": (d, n),
        "n": n,
        "phi": phi
    }


# ── RSA operations ─────────────────────────

def encrypt(message, public_key):
    e, n = public_key
    if not (0 <= message < n):
        raise ValueError("message hors intervalle")
    return pow(message, e, n)


def decrypt(ciphertext, private_key):
    d, n = private_key
    return pow(ciphertext, d, n)


def sign(message, private_key):
    d, n = private_key
    if not (0 <= message < n):
        raise ValueError("message hors intervalle")
    return pow(message, d, n)


def verify(message, signature, public_key):
    e, n = public_key
    return pow(signature, e, n) == message
