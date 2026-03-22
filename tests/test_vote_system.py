
import hashlib
import pytest

## utilisation de base de donnes simules juste pour tester 


voters_db = {}
votes = {}

##ajouter un votant 


def add_voter(n1, n2):
    hash_n2 = hashlib.sha256(n2.encode()).hexdigest()
    voters_db[n1] = {
        "n2_hash": hash_n2,
        "has_voted": False,
        "n2_plain": n2  # stocker N2 clair pour les tests
    }

 ### creation de votans fictifs 

add_voter("VOTANT001", "CODEA12345")
add_voter("VOTANT002", "CODEB67890")
add_voter("VOTANT003", "CODEC54321")
add_voter("VOTANT004", "CODED09876")
add_voter("VOTANT005", "CODEE11223")


## les testes dans cette partie ajouter dans le code mais , pour qu 'il s'affiche pour l'utilisateur 
 ## verifier N1   et le double vote 



def verify_n1(n1):
    if n1 not in voters_db:
        return False, "N1 invalide"
    if voters_db[n1]["has_voted"]:
        return False, "Ce votant a déjà voté"
    return True, "N1 valide"



# Soumettre un vote et tester si N2 et valide ou pas , aussi tester le score il doit etre entre 1 et 10 


def submit_vote(n1, n2, score):
    ok, msg = verify_n1(n1)
    if not ok:
        return False, msg

    hash_n2_votant = hashlib.sha256(n2.encode()).hexdigest()
    if hash_n2_votant != voters_db[n1]["n2_hash"]:
        return False, "N2 invalide"

    if score < 0 or score > 10:
        return False, "Score invalide"

    votes[n2] = score
    voters_db[n1]["has_voted"] = True
    return True, "Vote enregistré"


# afficher les resultats 

def show_results():
    print("\nVotes enregistrés :\n")
    if not votes:
        print("Aucun vote pour le moment.")
        return
    for code, score in votes.items():
        print(code, "->", score)




def process_vote(n1, n2, score):
    success, msg = submit_vote(n1, n2, score)
    return success, msg



# les tests avec pytest. ( ajouter  dans le dossier tests , des tests automatique  )


@pytest.fixture(autouse=True)
def reset_data():
    voters_db.clear()
    votes.clear()
    add_voter("VOTANT001", "CODEA12345")
    add_voter("VOTANT002", "CODEB67890")
    add_voter("VOTANT003", "CODEC54321")

# tester les N1 Valides 


def test_all_n1_valid():
    for n1 in voters_db.keys():
        ok, _ = verify_n1(n1)
        assert ok is True

@pytest.mark.parametrize("fake_n1", ["FAKE1", "TEST", "", None])
def test_invalid_n1(fake_n1):
    ok, _ = verify_n1(fake_n1)
    assert ok is False

# tester les N1 et N2 valides pour effectuer  le vote .
def test_all_valid_votes():
    for n1, data in voters_db.items():
        n2 = data["n2_plain"]
        success, _ = submit_vote(n1, n2, 5)
        assert success is True

#tester les N2 valides 


def test_all_wrong_n2():
    for n1 in voters_db.keys():
        success, _ = submit_vote(n1, "WRONGCODE", 5)
        assert success is False


## tester le double vote chaque , chaque votant a le droit de voter une seule fois .

def test_double_vote_global():
    for n1, data in voters_db.items():
        n2 = data["n2_plain"]
        submit_vote(n1, n2, 5)
        success, _ = submit_vote(n1, n2, 6)
        assert success is False

  ## tester le score , il doit etre entre 1 et 10 .      

@pytest.mark.parametrize("bad_score", [-10, -1, 11, 100])
def test_invalid_scores(bad_score):
    for n1, data in voters_db.items():
        n2 = data["n2_plain"]
        success, _ = submit_vote(n1, n2, bad_score)
        assert success is False
