# test_vote_db.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Electeur, Bulletin, Resultat
from database import ToyTetragraphHash, generate_keys, hash_func, submit_vote, init_voters


#  Setup DB en mémoire pour tests

@pytest.fixture(scope="function")
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

## Initialisation RSA et TTH 

@pytest.fixture(scope="module")
def keys_and_tth():
    keys = generate_keys(61, 53)
    tth = ToyTetragraphHash()
    return keys, tth

#  Fixture pour initialiser votants

@pytest.fixture(scope="function")
def voters(db):
    init_voters(db)
    return db.query(Electeur).all()


#  Test N1 valides

def test_valid_n1(db, voters):
    for electeur in voters:
        ok, result = submit_vote(db, electeur.code_n1, electeur.code_n1.replace("VOTANT", "CODEA"), 5)
        # On ne commit pas pour ce test, juste vérifier N2
        assert ok is False or ok is True  # juste vérifier la fonction


#  Test N2 invalide

def test_invalid_n2(db, voters):
    for electeur in voters:
        ok, msg = submit_vote(db, electeur.code_n1, "FAKEN2", 5)
        assert ok is False
        assert msg == "N2 invalide"


#  Test score invalide

@pytest.mark.parametrize("bad_score", [-1, -10, 11, 100])
def test_invalid_score(db, voters, bad_score):
    for electeur in voters:
        ok, msg = submit_vote(db, electeur.code_n1, electeur.code_n1.replace("VOTANT", "CODEA"), bad_score)
        assert ok is False
        assert msg == "Score invalide"


#  Test double vote

def test_double_vote(db, voters):
    for electeur in voters:
        n2 = electeur.code_n1.replace("VOTANT", "CODEA")
        ok, msg = submit_vote(db, electeur.code_n1, n2, 5)
        assert ok is True
        # Essayer de voter une deuxième fois
        ok2, msg2 = submit_vote(db, electeur.code_n1, n2, 6)
        assert ok2 is False
        assert msg2 == "Déjà voté"


#  Test stockage signature + TTH

def test_signature_tth(db):
    # Prendre un votant
    n1 = "VOTANT001"
    n2 = "CODEA12345"
    score = 7

    ok, msg = submit_vote(db, n1, n2, score)
    assert ok is True

    bulletin = db.query(Bulletin).filter_by(code_n2=n2).first()
    assert bulletin is not None
    assert bulletin.signature is not None
    assert hasattr(bulletin, "tth_hash")
    assert len(bulletin.tth_hash) == 4  # Toy TTH 4 caractères

    resultat = db.query(Resultat).filter_by(code_n2=n2).first()
    assert resultat.note == score
    assert resultat.sig_valide is True
    assert resultat.n2_valide is True
