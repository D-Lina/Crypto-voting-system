from utils.audit_log import log_action

"""
    Anonymizer — the ballot box of the protocol.

    Responsibilities:
      - Verify voter eligibility via the commissioner (verify_n1)
      - Consume the N1 code to enforce one-vote-per-voter (consume_n1)
      - Store the ballot WITHOUT the N1 code — this severs the link
        between voter identity and ballot content
      - Hand the full ballot box to the counter after voting closes

    The anonymizer sees the N1 code at submission time but deliberately
    never stores it alongside the ballot. It cannot read the vote content
    because the ballot arrives encrypted with the counter's public key.
"""
class Anonymizer:
    def __init__(self):
        self._commissioner = None
        self._ballot_box: list[dict] = []

    ## Setup here is simpler cause it relies on commissioner, no unique keypair
    def setup(self, commissioner) -> None:
        self._commissioner = commissioner
        log_action("Anonymizer setup", {})

    ## Three things happen in strict order:
    ## Step 1 — verify N1 with the commissioner. Read-only check first to avoid consuming codes from ineligible voters.
    ## Step 2 — consume N1. irreversible step: the commissioner removes the code from the valid list. 
    # After this point the voter cannot vote again.
    ## Step 3 — store the ballot without N1. The dict stored matches the Bulletin model.
    def receive_ballot(self, n1: str, vote_chiffre: int, signature: int, code_n2: str) -> bool:
        if not self._commissioner.verify_n1(n1):
            log_action("Ballot rejected", {"reason": "invalid or unknown N1"})
            return False

        if not self._commissioner.consume_n1(n1):
            log_action("Ballot rejected", {"reason": "N1 already used"})
            return False

        ballot = {
            "vote_chiffre": vote_chiffre,
            "signature":    str(signature),
            "code_n2":      code_n2
        }
        self._ballot_box.append(ballot)
        log_action("Ballot accepted", {"code_n2": code_n2})
        return True
    
    ## Called by the VotingSession later after the election closes, returns the full ballot box for counting.
    def get_ballots(self) -> list[dict]:
        return self._ballot_box