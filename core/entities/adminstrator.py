from crypto.rsa import generate_keys
from crypto.blind_signature import blind_sign
from utils.audit_log import log_action

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
