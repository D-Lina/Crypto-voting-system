from core.utils.audit_log import log_action
from databases.database import SessionLocal
from databases.models import Bulletin


class Anonymizer:
    """
    Now stores ballots in the database instead of memory.
    """

    def __init__(self):
        self._commissioner = None
        self.db = SessionLocal()

    def setup(self, commissioner) -> None:
        self._commissioner = commissioner
        log_action("Anonymizer setup", {})

    def receive_ballot(self, n1: str, vote_chiffre: int, signature: int, code_n2: str) -> bool:
        """
        - Verify N1
        - Consume N1
        - Store ballot WITHOUT N1 (preserve anonymity)
        """

        if not self._commissioner.verify_n1(n1):
            log_action("Ballot rejected", {"reason": "invalid N1"})
            return False

        if not self._commissioner.consume_n1(n1):
            log_action("Ballot rejected", {"reason": "already used"})
            return False

        bulletin = Bulletin(
            vote_chiffre=str(vote_chiffre).encode(),
            signature=str(signature),
            code_n2=code_n2
        )

        self.db.add(bulletin)
        self.db.commit()

        log_action("Ballot stored in DB", {"code_n2": code_n2})
        return True

    def get_ballots(self):
        """
        Retrieve ballots from DB for counting
        """
        bulletins = self.db.query(Bulletin).all()

        return [
            {
                "vote_chiffre": int(b.vote_chiffre.decode()),
                "signature": b.signature,
                "code_n2": b.code_n2
            }
            for b in bulletins
        ]
