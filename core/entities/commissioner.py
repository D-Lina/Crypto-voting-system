from core.crypto.tth_hash import ToyTetragraphHash
from core.utils.audit_log import log_action
from databases.database import SessionLocal
from databases.models import Electeur


class Commissioner:
    """
    Commissioner now uses the database instead of in-memory sets.

    Responsibilities:
    - Check if N1 exists and has not voted
    - Mark N1 as used (a_vote = True)
    - Verify N2 via stored fingerprint
    """

    def __init__(self):
        self.db = SessionLocal()
        self.tth = ToyTetragraphHash()

    def setup(self, voters: list[dict]) -> None:
        """
        Store voters in DB (N1 + hashed N2)
        """
        for v in voters:
            fingerprint = self.tth.hash(v["n2"])

            electeur = Electeur(
                code_n1=v["n1"],
                empreinte_n2=fingerprint,
                a_vote=False
            )

            self.db.add(electeur)

        self.db.commit()

        log_action("Commissioner setup (DB)", {"count": len(voters)})

    def verify_n1(self, n1: str) -> bool:
        """
        Check if voter exists and has not voted
        """
        electeur = self.db.query(Electeur).filter_by(code_n1=n1).first()

        result = electeur is not None and not electeur.a_vote

        log_action("N1 verification", {"n1": n1, "result": result})
        return result

    def consume_n1(self, n1: str) -> bool:
        """
        Mark voter as having voted
        """
        electeur = self.db.query(Electeur).filter_by(code_n1=n1).first()

        if not electeur or electeur.a_vote:
            log_action("N1 consume rejected", {"n1": n1})
            return False

        electeur.a_vote = True
        self.db.commit()

        log_action("N1 consumed", {"n1": n1})
        return True

    def verify_n2_fingerprint(self, n2: str) -> bool:
        """
        Verify N2 using stored fingerprint
        """
        fingerprint = self.tth.hash(n2)

        electeur = self.db.query(Electeur).filter_by(
            empreinte_n2=fingerprint
        ).first()

        result = electeur is not None

        log_action("N2 verification", {"fingerprint": fingerprint, "result": result})
        return result
