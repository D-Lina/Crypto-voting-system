import random

def generate_blinding_factor(n):
    return random.randint(2, n - 1)


def blind_message(message, public_key):
    e, n = public_key
    
    r = generate_blinding_factor(n)
    blinded = (message * pow(r, e, n)) % n
    
    return blinded, r


def blind_sign(blinded_message, private_key):
    d, n = private_key
    return pow(blinded_message, d, n)


def unblind_signature(blind_signature, r, public_key):
    n = public_key[1]
    
    r_inv = pow(r, -1, n)
    signature = (blind_signature * r_inv) % n
    
    return signature
