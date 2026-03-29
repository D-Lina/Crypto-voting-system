import pytest
from core.entities.commissioner import Commissioner
from core.crypto.tth_hash import ToyTetragraphHash


@pytest.fixture
def comm():
    tth = ToyTetragraphHash()

    # Real N2 codes
    n2_1 = "CODEA12345"
    n2_2 = "CODEB67890"

    c = Commissioner()
    c.setup(
        n1_codes={"AAA111BBB222", "CCC333DDD444"},
        n2_fingerprints={tth.hash(n2_1), tth.hash(n2_2)}
    )

    return c, n2_1, n2_2


def test_verify_n1_valid(comm):
    c, _, _ = comm
    assert c.verify_n1("AAA111BBB222") is True


def test_verify_n1_invalid(comm):
    c, _, _ = comm
    assert c.verify_n1("ZZZZZZZZZZZZ") is False


def test_consume_n1_removes_it(comm):
    c, _, _ = comm
    assert c.consume_n1("AAA111BBB222") is True
    assert c.verify_n1("AAA111BBB222") is False  # removed


def test_consume_n1_twice_fails(comm):
    c, _, _ = comm
    c.consume_n1("AAA111BBB222")
    assert c.consume_n1("AAA111BBB222") is False


def test_verify_n2_fingerprint_valid(comm):
    c, n2_1, _ = comm
    assert c.verify_n2_fingerprint(n2_1) is True


def test_verify_n2_fingerprint_invalid(comm):
    c, _, _ = comm
    assert c.verify_n2_fingerprint("RANDOM_GARBAGE_N2") is False
