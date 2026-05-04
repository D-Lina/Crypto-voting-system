import os
import sys
from contextlib import asynccontextmanager

import audit_store

import core.utils.audit_log as _al
_al.log_action = audit_store.log_action

from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional

from core.protocol.VotingSession import VotingSession
from core.protocol.voter import Voter
from core.crypto.tth_hash import ToyTetragraphHash

# Database imports
from databases.database import SessionLocal
from databases import models

ADMIN_PIN: str = os.getenv("ADMIN_PIN", "1234")

_session: VotingSession = VotingSession()
_voter_count: int = 0
_count_summary: Optional[dict] = None
_tth = ToyTetragraphHash()


def get_db():
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise


def _reset_session() -> None:
    global _session, _voter_count, _count_summary
    _session = VotingSession()
    _voter_count = 0
    _count_summary = None
    audit_store.reset_trail()

    # Clear database tables
    db = SessionLocal()
    try:
        db.query(models.Resultat).delete()
        db.query(models.Bulletin).delete()
        db.query(models.Electeur).delete()
        db.query(models.CleRSA).delete()
        db.commit()
    except Exception as e:
        db.rollback()
    finally:
        db.close()


def _require_pin(pin: Optional[str]) -> None:
    if pin != ADMIN_PIN:
        raise HTTPException(status_code=401, detail="Invalid or missing admin PIN")


def _admin_public_key() -> Optional[tuple]:
    try:
        keys = _session.get_public_keys()
        return keys.get("admin")
    except Exception:
        return None


def _counter_public_key() -> Optional[tuple]:
    try:
        keys = _session.get_public_keys()
        return keys.get("counter")
    except Exception:
        return None


app = FastAPI(title="CryptoVote API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class PinBody(BaseModel):
    pin: str


class VoterEntry(BaseModel):
    n1: str
    n2: str


class SetupBody(BaseModel):
    pin: str
    voters: list[VoterEntry]
    admin_primes: list[int]
    counter_primes: list[int]


class AdminActionBody(BaseModel):
    pin: str


class VoteBody(BaseModel):
    n1: str
    n2: str
    vote: int


@app.get("/election/status")
def election_status():
    return {
        "state": _session.state,
        "voter_count": _voter_count,
    }


@app.post("/admin/verify-pin")
def verify_pin(body: PinBody):
    _require_pin(body.pin)
    return {"ok": True}


@app.get("/admin/status")
def admin_status(x_admin_pin: Optional[str] = Header(default=None)):
    _require_pin(x_admin_pin)

    admin_pk = _admin_public_key()
    counter_pk = _counter_public_key()

    payload = {
        "state": _session.state,
        "voter_count": _voter_count,
        "admin_e": admin_pk[0] if admin_pk else None,
        "admin_n": admin_pk[1] if admin_pk else None,
        "counter_n": counter_pk[1] if counter_pk else None,
    }
    return payload


@app.post("/admin/setup")
def admin_setup(body: SetupBody):
    _require_pin(body.pin)

    if _session.state != "IDLE":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot setup: session is already in state '{_session.state}'"
        )

    if len(body.admin_primes) != 2 or len(body.counter_primes) != 2:
        raise HTTPException(status_code=400, detail="admin_primes and counter_primes must each have exactly 2 values")

    voters_data = [{"n1": v.n1, "n2": v.n2} for v in body.voters]

    try:
        _session.setup_election(
            voters=voters_data,
            admin_primes=tuple(body.admin_primes),
            counter_primes=tuple(body.counter_primes),
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    global _voter_count
    _voter_count = len(voters_data)

    # Save voters to database
    db = SessionLocal()
    try:
        for v in body.voters:
            n2_fingerprint = _tth.hash(v.n2)[:4]  # Store first 4 chars as fingerprint
            electeur = models.Electeur(
                code_n1=v.n1,
                empreinte_n2=n2_fingerprint,
                a_vote=False
            )
            db.merge(electeur)  # merge to avoid duplicate key errors on re-setup

        # Save RSA public keys
        admin_pk = _admin_public_key()
        counter_pk = _counter_public_key()

        if admin_pk:
            admin_key = models.CleRSA(
                entite="admin",
                cle_publique=str(admin_pk),
                cle_privee=""
            )
            db.merge(admin_key)

        if counter_pk:
            counter_key = models.CleRSA(
                entite="decompte",
                cle_publique=str(counter_pk),
                cle_privee=""
            )
            db.merge(counter_key)

        db.commit()
    except Exception as e:
        db.rollback()
    finally:
        db.close()

    admin_pk = _admin_public_key()
    counter_pk = _counter_public_key()

    return {
        "state": _session.state,
        "voter_count": _voter_count,
        "admin_e": admin_pk[0] if admin_pk else None,
        "admin_n": admin_pk[1] if admin_pk else None,
        "counter_n": counter_pk[1] if counter_pk else None,
    }


@app.post("/admin/close")
def admin_close(body: AdminActionBody):
    _require_pin(body.pin)

    try:
        _session.close_voting()
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {"state": _session.state}


@app.post("/admin/count")
def admin_count(body: AdminActionBody):
    _require_pin(body.pin)

    global _count_summary
    try:
        summary = _session.start_counting()
        _count_summary = summary
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # Save results to database
    db = SessionLocal()
    try:
        results = _session.get_results()
        for r in results:
            resultat = models.Resultat(
                code_n2=r["code_n2"],
                note=r["note"],
                sig_valide=r["sig_valide"],
                n2_valide=r["n2_valide"]
            )
            db.merge(resultat)
        db.commit()
    except Exception as e:
        db.rollback()
    finally:
        db.close()

    return {"state": _session.state, **summary}


@app.post("/admin/reset")
def admin_reset(body: AdminActionBody):
    _require_pin(body.pin)
    _reset_session()
    return {"state": "IDLE"}


@app.get("/admin/audit")
def admin_audit(x_admin_pin: Optional[str] = Header(default=None)):
    _require_pin(x_admin_pin)
    return {"trail": audit_store.get_trail()}


@app.post("/vote")
def cast_vote(body: VoteBody):
    if _session.state != "VOTING":
        raise HTTPException(
            status_code=400,
            detail=f"Voting is not open. Current state: {_session.state}"
        )

    if not (0 <= body.vote <= 10):
        raise HTTPException(status_code=400, detail="Vote must be between 0 and 10")

    admin_pk = _admin_public_key()
    counter_pk = _counter_public_key()

    if admin_pk is None or counter_pk is None:
        raise HTTPException(status_code=500, detail="Public keys not initialised")

    v = Voter(body.n1, body.n2)

    try:
        accepted = v.cast_vote(
            vote=body.vote,
            administrator=_session.administrator,
            anonymizer=_session.anonymizer,
            admin_public_key=admin_pk,
            counter_public_key=counter_pk,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    if not accepted:
        raise HTTPException(
            status_code=400,
            detail="Ballot rejected — invalid N1 or already voted"
        )

    # Save ballot to database
    db = SessionLocal()
    try:
        # Get the last ballot from anonymizer (the one just submitted)
        ballots = _session.anonymizer.get_ballots()
        if ballots:
            last_ballot = ballots[-1]
            bulletin = models.Bulletin(
                vote_chiffre=last_ballot["vote_chiffre"].to_bytes(
                    (last_ballot["vote_chiffre"].bit_length() + 7) // 8, "big"
                ),
                signature=last_ballot["signature"],
                code_n2=last_ballot["code_n2"]
            )
            db.add(bulletin)

        # Mark voter as having voted
        electeur = db.query(models.Electeur).filter(
            models.Electeur.code_n1 == body.n1
        ).first()
        if electeur:
            electeur.a_vote = True

        db.commit()
    except Exception as e:
        db.rollback()
    finally:
        db.close()

    return {"ok": True}


@app.get("/results")
def get_results():
    if _session.state != "COUNTED":
        return {"state": _session.state}

    summary = _count_summary or {}
    raw_tally: dict = summary.get("tally", {})

    tally = [{"vote": int(k), "count": int(v)} for k, v in raw_tally.items()]
    tally.sort(key=lambda x: x["vote"])

    raw_ballots = []
    try:
        raw_ballots = _session.get_results()
    except Exception:
        pass

    ballots = [
        {
            "n2": b.get("code_n2", ""),
            "vote": b.get("note"),
            "sig_valid": bool(b.get("sig_valide", False)),
            "n2_valid": bool(b.get("n2_valide", False)),
            "status": "ACCEPTED" if (b.get("sig_valide") and b.get("n2_valide")) else "REJECTED",
        }
        for b in raw_ballots
    ]

    return {
        "state": _session.state,
        "tally": tally,
        "total": summary.get("total", 0),
        "valid": summary.get("valid", 0),
        "invalid": summary.get("invalid", 0),
        "ballots": ballots,
    }
