import pytest
from entities.commissioner import Commissioner

@pytest.fixture
def comm():
    c = Commissioner()
    c.setup(
        n1_codes={"AAA111BBB222", "CCC333DDD444"},
        n2_fingerprints={"HASH1", "HASH2"}   # use real TTH outputs once you compute them
    )
    return c

def test_verify_n1_valid(comm):
    assert comm.verify_n1("AAA111BBB222") is True

def test_verify_n1_invalid(comm):
    assert comm.verify_n1("ZZZZZZZZZZZZ") is False

def test_consume_n1_removes_it(comm):
    assert comm.consume_n1("AAA111BBB222") is True
    assert comm.verify_n1("AAA111BBB222") is False   # gone

def test_consume_n1_twice_fails(comm):
    comm.consume_n1("AAA111BBB222")
    assert comm.consume_n1("AAA111BBB222") is False  # second attempt fails

def test_verify_n2_fingerprint_valid(comm):
    # pick a real n2 that hashes to "HASH1" in your TTH
    assert comm.verify_n2_fingerprint("some_n2_that_produces_HASH1") is True

def test_verify_n2_fingerprint_invalid(comm):
    assert comm.verify_n2_fingerprint("RANDOM_GARBAGE_N2") is False