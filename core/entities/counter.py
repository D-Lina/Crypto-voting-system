from crypto.rsa import generate_keys, decrypt, verify
from utils.audit_log import log_action
from utils.blind_utils import hash_message
"""
    Vote counter — decrypts and validates ballots after the election closes.

    Responsibilities:
      - Hold its own RSA keypair (public key used by voters to encrypt ballots)
      - Decrypt ballots using its private key (open the envelope)
      - Verify each ballot's signature using the administrator's public key
      - Validate each ballot's N2 code via the commissioner
      - Tally valid votes and log every result for the audit trail

    The counter knows the vote content and N2 code but cannot link
    either back to a specific voter — the anonymizer severed that link.
"""
class Counter:
    def __init__(self):
        self._keys: dict = None
        self._commissioner = None
        self._admin_public_key: tuple = None
        self._results: list[dict] = []
    
    ## 4 arguments: - the commissioner instance,
    ## - the admin's public key tuple (e, n)
    ## - and two primes for its own RSA keypair.
    def setup(self, commissioner, admin_public_key: tuple, p: int, q: int) -> None:
        self._commissioner = commissioner
        self._admin_public_key = admin_public_key
        self._keys = generate_keys(p, q)
        log_action("Counter setup", {
            "public_key": self._keys["public"]
        })
    
    def get_public_key(self) -> tuple:
        return self._keys["public"]
    
    ## Calls decrypt from RSA.py
    def decrypt_ballot(self, vote_chiffre: int) -> int:
        return decrypt(vote_chiffre, self._keys["private"])
    
    ## Calls verify from RSA.py
    from utils.blind_utils import hash_message

    def verify_ballot_signature(self, note: int, signature: int) -> bool:
     e, n = self._admin_public_key
     hashed_note = hash_message(note) % n   # 🔥 IMPORTANT FIX
     return pow(signature, e, n) == hashed_note
    
    ## MAIN COUNTER FUNCTION, matches the "Resultat" form
    def count_ballots(self, ballots: list[dict]) -> dict:
        self._results = []
        tally = {}
        valid_count = 0
        invalid_count = 0

        for ballot in ballots:
            note = self.decrypt_ballot(ballot["vote_chiffre"])
            sig_valide = self.verify_ballot_signature(note, int(ballot["signature"]))
            n2_valide = self._commissioner.verify_n2_fingerprint(ballot["code_n2"])

            result = {
                "code_n2":   ballot["code_n2"],
                "note":      note,
                "sig_valide": sig_valide,
                "n2_valide":  n2_valide
            }
            self._results.append(result)

            if sig_valide and n2_valide:
                tally[note] = tally.get(note, 0) + 1
                valid_count += 1
            else:
                invalid_count += 1

            log_action("Ballot counted", result)

        summary = {
            "tally":   tally,
            "valid":   valid_count,
            "invalid": invalid_count,
            "total":   valid_count + invalid_count
        }
        log_action("Counting complete", summary)
        return summary
    
    ## Returns (N2, Vote) pair
    ## THIS WHAT ALLOW THE VOTER TO VERIFY THEIR VOTE HAS BEEN COUNTED
    def get_results(self) -> list[dict]:
        return self._results
