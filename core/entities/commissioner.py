from crypto.tth_hash import ToyTetragraphHash
from utils.audit_log import log_action

class Commissioner:
    """
    Voting commissioner — the trust anchor of the protocol.

    Responsibilities:
      - Hold the valid N1 code list (voter roll)
      - Hold the hashed N2 fingerprint list (ballot authenticity)
      - Confirm voter eligibility (verify_n1)
      - Enforce one-vote-per-voter (consume_n1)
      - Validate N2 codes during counting (verify_n2_fingerprint)

    The commissioner never sees raw N2 codes, only their TTH fingerprints.
    The commissioner never sees ballot content, only code validations.
    """

    def __init__(self):
        self._valid_n1: set[str] = set()
        self._valid_n2_fingerprints: set[str] = set()
        self._tth = ToyTetragraphHash()

    def setup(self, n1_codes: set[str], n2_fingerprints: set[str]) -> None:
        """Initialize the commissioner with valid N1 codes and N2 fingerprints."""
        self._valid_n1 = set(n1_codes)
        self._valid_n2_fingerprints = set(n2_fingerprints)
        log_action("Election setup", {
            "n1_count": len(self._valid_n1),
            "n2_fingerprint_count": len(self._valid_n2_fingerprints)
        })

    def verify_n1(self, n1: str) -> bool:
        """Check if N1 code is valid (eligible voter)."""
        result = n1 in self._valid_n1
        log_action("N1 verification", {"n1": n1, "result": result})
        return result

    def consume_n1(self, n1: str) -> bool:
        """Mark N1 as used to enforce one-vote-per-voter."""
        if n1 not in self._valid_n1:
            log_action("N1 consume rejected", {"n1": n1, "reason": "not found or already used"})
            return False
        self._valid_n1.discard(n1)
        log_action("N1 consumed", {"n1": n1})
        return True

    def verify_n2_fingerprint(self, n2: str) -> bool:
        """Verify that N2 code fingerprint matches a valid one."""
        fingerprint = self._tth.hash(n2)
        result = fingerprint in self._valid_n2_fingerprints
        log_action("N2 fingerprint verification", {
            "fingerprint": fingerprint,
            "result": result
        })
        return result
