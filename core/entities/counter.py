from crypto.rsa import generate_keys, decrypt, verify
from utils.audit_log import log_action
from database.database import SessionLocal
from database.models import Resultat


class Counter:
    """
    Now stores counting results in DB.
    """

    def __init__(self):
        self._keys = None
        self._commissioner = None
        self._admin_public_key = None
        self.db = SessionLocal()

    def setup(self, commissioner, admin_public_key, p: int, q: int):
        self._commissioner = commissioner
        self._admin_public_key = admin_public_key
        self._keys = generate_keys(p, q)

    def get_public_key(self):
        return self._keys["public"]

    def decrypt_ballot(self, vote_chiffre: int) -> int:
        return decrypt(vote_chiffre, self._keys["private"])

    def verify_ballot_signature(self, note: int, signature: int) -> bool:
        return verify(note, signature, self._admin_public_key)

    def count_ballots(self, ballots):
        tally = {}
        valid = 0
        invalid = 0

        for ballot in ballots:
            note = self.decrypt_ballot(ballot["vote_chiffre"])

            sig_valide = self.verify_ballot_signature(note, int(ballot["signature"]))
            n2_valide = self._commissioner.verify_n2_fingerprint(ballot["code_n2"])

            result = Resultat(
                code_n2=ballot["code_n2"],
                note=note,
                sig_valide=sig_valide,
                n2_valide=n2_valide
            )

            self.db.add(result)

            if sig_valide and n2_valide:
                tally[note] = tally.get(note, 0) + 1
                valid += 1
            else:
                invalid += 1

        self.db.commit()

        summary = {
            "tally": tally,
            "valid": valid,
            "invalid": invalid,
            "total": valid + invalid
        }

        log_action("Counting complete", summary)
        return summary

    def get_results(self):
        """
        Fetch results from DB
        """
        return self.db.query(Resultat).all()
