from crypto.blind_signature import blind_message, unblind_signature
from crypto.rsa import encrypt
from utils.blind_utils import hash_message
from utils.utils import convert_vote_to_int, validate_vote
from utils.audit_log import log_action


class Voter:
    """
    Voter-side protocol actor.

    Responsibilities:
      - Hold the voter's N1 and N2 codes
      - Prepare the vote value
      - Blind the vote before sending it to the administrator
      - Request a blind signature from the administrator
      - Unblind the returned signature
      - Encrypt the vote for the counter
      - Submit the final ballot to the anonymizer
    """

    def __init__(self, n1: str, n2: str):
        self.n1 = n1
        self.n2 = n2

        self.vote = None
        self.blinded_vote = None
        self.blinding_factor = None
        self.signature = None
        self.vote_chiffre = None

    ## Convert and validate the vote before any crypto step, returns the normalized integer vote.
    def set_vote(self, vote) -> int:
        vote_int = convert_vote_to_int(vote)
        validate_vote(vote_int)

        self.vote = vote_int
        log_action("Vote selected", {"n1": self.n1, "vote": self.vote})
        return self.vote

    ## Blind the vote using the administrator's public key, returns the blinded vote as an integer.
    def blind_vote(self, admin_public_key: tuple) -> int:
        if self.vote is None:
            raise ValueError("Vote must be set before blinding.")

        blinded, r = blind_message(
            message=self.vote,
            public_key=admin_public_key,
            hash_func=hash_message
        )

        self.blinded_vote = blinded
        self.blinding_factor = r

        log_action("Vote blinded", {
            "n1": self.n1,
            "blinded_vote": self.blinded_vote
        })
        return self.blinded_vote
    
    ## Request the administrator to blind-sign the blinded vote, The raw blind signature returned by the administrator.
    def request_signature(self, administrator) -> int:
        if self.blinded_vote is None:
            raise ValueError("Vote must be blinded before requesting a signature.")

        blind_sig = administrator.request_blind_signature(self.blinded_vote)

        log_action("Blind signature received", {
            "n1": self.n1,
            "blinded_vote": self.blinded_vote
        })
        return blind_sig
    
    ## Remove the blinding factor from the administrator's blind signature, returns the unblinded signature as an integer.
    def unblind_signature(self, blind_sig: int, admin_public_key: tuple) -> int:
        if self.blinding_factor is None:
            raise ValueError("No blinding factor available. Blind the vote first.")

        self.signature = unblind_signature(
            blind_signature=blind_sig,
            r=self.blinding_factor,
            public_key=admin_public_key
        )

        log_action("Signature unblinded", {
            "n1": self.n1,
            "signature": self.signature
        })
        return self.signature
    
    ## Encrypt the vote for the counter, returns the encrypted vote as an integer.
    def encrypt_vote(self, counter_public_key: tuple) -> int:
        if self.vote is None:
            raise ValueError("Vote must be set before encryption.")

        self.vote_chiffre = encrypt(self.vote, counter_public_key)

        log_action("Vote encrypted", {
            "n1": self.n1,
            "vote_chiffre": self.vote_chiffre
        })
        return self.vote_chiffre

    ## Submit the final ballot to the anonymizer, returns True if accepted, False otherwise.
    def submit_ballot(self, anonymizer) -> bool:
        if self.vote_chiffre is None:
            raise ValueError("Vote must be encrypted before submission.")
        if self.signature is None:
            raise ValueError("Signature must be available before submission.")

        accepted = anonymizer.receive_ballot(
            n1=self.n1,
            vote_chiffre=self.vote_chiffre,
            signature=self.signature,
            code_n2=self.n2
        )

        log_action("Ballot submitted", {
            "n1": self.n1,
            "accepted": accepted
        })
        return accepted
    
    ## The full voting protocol in one method, for convenience. Each step can also be called separately if needed.
    """
        Steps:
          1. set the vote
          2. blind the vote
          3. request administrator signature
          4. unblind the signature
          5. encrypt the vote for the counter
          6. submit the ballot to the anonymizer
    """
    def cast_vote(self, vote, administrator, anonymizer, admin_public_key: tuple, counter_public_key: tuple) -> bool:

        self.set_vote(vote)
        self.blind_vote(admin_public_key)
        blind_sig = self.request_signature(administrator)
        self.unblind_signature(blind_sig, admin_public_key)
        self.encrypt_vote(counter_public_key)
        return self.submit_ballot(anonymizer)
