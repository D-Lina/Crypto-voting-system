import pytest
from core.entities.commissioner import Commissioner
from core.entities.administrator import Administrator

@pytest.fixture
def setup():
    comm = Commissioner()
    comm.setup(n1_codes={"VALIDCODE0001"}, n2_fingerprints=set())
    admin = Administrator()
    admin.setup(commissioner=comm, p=61, q=53)
    admin.open_election()   
    return admin, comm

def test_get_public_key_returns_tuple(setup):
    admin, _ = setup
    e, n = admin.get_public_key()
    assert isinstance(e, int) and isinstance(n, int)

def test_verify_voter_eligibility_valid(setup):
    admin, _ = setup
    assert admin.verify_voter_eligibility("VALIDCODE0001") is True

def test_verify_voter_eligibility_invalid(setup):
    admin, _ = setup
    assert admin.verify_voter_eligibility("DOESNOTEXIST") is False

def test_blind_sign_returns_int_when_open(setup):
    admin, _ = setup
    result = admin.request_blind_signature(blinded_message=42)
    assert isinstance(result, int)

def test_blind_sign_fails_when_closed(setup):
    admin, _ = setup
    admin.close_election()
    with pytest.raises(Exception):   # whatever error you raise when closed
        admin.request_blind_signature(blinded_message=42)

def test_close_then_open_restores_signing(setup):
    admin, _ = setup
    admin.close_election()
    admin.open_election()
    result = admin.request_blind_signature(blinded_message=42)
    assert isinstance(result, int)
