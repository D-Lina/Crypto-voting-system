from core.crypto.rsa import generate_keys
from core.crypto.blind_signature import blind_sign
from core.utils.audit_log import log_action

"""
    Election administrator — issues authenticated ballots via blind signatures.

    Responsibilities:
      - Hold the RSA keypair (public key shared with voters and counter)
      - Confirm voter eligibility by delegating to the commissioner
      - Blind-sign ballots without ever seeing their content
      - Refuse all signing once the election is closed

    The administrator never sees N2 codes and cannot link a signature
    to a specific voter because the ballot was blinded before submission.
"""
class Administrator:
    def __init__(self):
        self._keys: dict = None
        self._commissioner = None
        self._election_open: bool = False

    ## Calls RSA.py to generate the key pair for the administrator    
    def setup(self, commissioner, p: int, q: int) -> None:
            self._commissioner = commissioner
            self._keys = generate_keys(p, q)
            log_action("Administrator setup", {
                "public_key": self._keys["public"]
            })

    ## Returns the (e, n) tuple representing the public key of the administrator
    def get_public_key(self) -> tuple:
        return self._keys["public"]
    
    ## Opens the election for voting, allowing voters to request blind signatures
    ## Closing it prevents any further signing and effectively ends the voting phase, 
    ## ensuring that no new ballots can be authenticated after the election is closed.
    def open_election(self) -> None:
        self._election_open = True
        log_action("Election opened", {})

    def close_election(self) -> None:
        self._election_open = False
        log_action("Election closed", {})

    ## Verifies voter eligibility relying on the commissioner and, if eligible, blind-signs the ballot.
    def verify_voter_eligibility(self, n1: str) -> bool:
        result = self._commissioner.verify_n1(n1)
        log_action("Voter eligibility check", {"n1": n1, "eligible": result})
        return result
    def request_blind_signature(self, blinded_message: int) -> int:
        if not self._election_open:
            raise PermissionError("Election is closed. No new signatures allowed.")
        signed = blind_sign(blinded_message, self._keys["private"])
        log_action("Blind signature issued", {"blinded_message": blinded_message})
        return signed
    
