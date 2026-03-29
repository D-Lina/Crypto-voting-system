from core.entities.commissioner import Commissioner
from core.entities.administrator import Administrator
from core.entities.anonymizer import Anonymizer
from core.entities.counter import Counter
from core.crypto.tth_hash import ToyTetragraphHash
from core.utils.audit_log import log_action

"""
## State machine
The session moves through four states in strict order.
IDLE → SETUP → VOTING → CLOSED → COUNTED
"""
class VotingSession:
    def __init__(self):
        self.commissioner  = Commissioner()
        self.administrator = Administrator()
        self.anonymizer    = Anonymizer()
        self.counter       = Counter()
        self._tth          = ToyTetragraphHash()
        self.state         = "IDLE"
    
    """
    Initialize all entities and open the election.
        The sequence matters:
            Commissioner first, everyone else depends on it
            Administrator second, needs commissioner, produces public key for counter
            Counter third, needs commissioner AND admin's public key
            Anonymizer last, only needs commissioner

    voters         -> list of {"n1": str, "n2": str} dicts (raw codes)
    admin_primes   -> (p, q) tuple for the administrator's RSA keypair
    counter_primes -> (p, q) tuple for the counter's RSA keypair

    N2 fingerprints are computed here with TTH, raw N2 codes are
    never stored anywhere after this method returns.
    """
    def setup_election(self, voters: list[dict], admin_primes: tuple, counter_primes: tuple) -> None:
        if self.state != "IDLE":
            raise RuntimeError(f"Cannot setup: session is in state '{self.state}'")

        n1_codes        = {v["n1"] for v in voters}
        n2_fingerprints = {self._tth.hash(v["n2"]) for v in voters}

        self.commissioner.setup(n1_codes, n2_fingerprints)
        self.administrator.setup(self.commissioner, *admin_primes)
        self.counter.setup(
            self.commissioner,
            self.administrator.get_public_key(),
            *counter_primes
        )
        self.anonymizer.setup(self.commissioner)
        self.administrator.open_election()

        self.state = "VOTING"
        log_action("Election setup complete", {
            "voter_count": len(voters),
            "state": self.state
        })

    ## Returns both public keys needed by voters before they can vote.
          # - admin   : (e, n) used to blind the ballot
          # - counter : (e, n) used to encrypt the ballot
    def get_public_keys(self) -> dict:
        return {
            "admin":   self.administrator.get_public_key(),
            "counter": self.counter.get_public_key()
        }

    ## Closes the election. 
    # After this point administrator.request_blind_signature() will raise PermissionError.
    def close_voting(self) -> None:
        if self.state != "VOTING":
            raise RuntimeError(f"Cannot close: session is in state '{self.state}'")
        self.administrator.close_election()
        self.state = "CLOSED"
        log_action("Voting closed", {"state": self.state})

    ## Passes the anonymizer's ballot box to the counter and returns the summary dictionary.
    def start_counting(self) -> dict:
        if self.state != "CLOSED":
            raise RuntimeError(f"Cannot count: session is in state '{self.state}'")
        ballots = self.anonymizer.get_ballots()
        results = self.counter.count_ballots(ballots)
        self.state = "COUNTED"
        log_action("Counting complete", {"state": self.state, **results})
        return results

    ## Returns per-ballot results for public verification.
    def get_results(self) -> list[dict]:

        if self.state != "COUNTED":
            raise RuntimeError(f"Results not available: session is in state '{self.state}'")
        return self.counter.get_results()
