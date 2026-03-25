from crypto.tth_hash import ToyTetragraphHash
from utils.audit_log import log_action

class Commissioner:
    def __init__(self):
        self.valid_n1: set[str] = set()
        self.valid_n2_fingerprints: set[str] = set()
        self.tth = ToyTetragraphHash()

        def setup(self, n1_codes: set[str], n2_fingerprints: set[str]) -> None:
            self._valid_n1 = set(n1_codes)
            self._valid_n2_fingerprints = set(n2_fingerprints)
            log_action("Election setup", {
                "n1_count": len(self._valid_n1),
                "n2_fingerprint_count": len(self._valid_n2_fingerprints)
            })

