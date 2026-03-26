import hashlib


from rsa_module import generate_keys, verify
from blind_signature import blind_message, blind_sign, unblind_signature
from tth_hash import ToyTetragraphHash

from database import SessionLocal
from models import Electeur, Bulletin, Resultat

print("SYSTEME AVEC DB + BLIND SIGNATURE + TTH")

## Initialisation RSA 

keys = generate_keys(61, 53)
public_key = keys["public"]
private_key = keys["private"]

tth = ToyTetragraphHash()

##  Hash pour RSA 


def hash_func(m):
    return int(hashlib.sha256(str(m).encode()).hexdigest(), 16) % public_key[1]

## Ajouter un votant dans la base de donnes 

def add_voter(db, n1, n2):
    empreinte = tth.hash(n2)

    electeur = Electeur(
        code_n1=n1,
        empreinte_n2=empreinte,
        a_vote=False
    )

    db.add(electeur)
    db.commit()

## Initialiser les votans (une fois )

def init_voters(db):
    if db.query(Electeur).first():
        return  # déjà rempli

    add_voter(db, "VOTANT001", "CODEA12345")
    add_voter(db, "VOTANT002", "CODEB67890")
    add_voter(db, "VOTANT003", "CODEC54321")
    add_voter(db, "VOTANT004", "CODED09876")
    add_voter(db, "VOTANT005", "CODEE11223")

## verifier N1 dans la base de donnes 


def verify_n1(db, n1):
    electeur = db.query(Electeur).filter_by(code_n1=n1).first()

    if not electeur:
        return False, "N1 invalide"

    if electeur.a_vote:
        return False, "Déjà voté"

    return True, electeur

 ## soumettre le vote dans la base de donnes 


def submit_vote(db, n1, n2, score):
    ok, result = verify_n1(db, n1)
    if not ok:
        return False, result

    electeur = result

    # Vérifier N2 avec TTH  


    empreinte = tth.hash(n2)
    if empreinte != electeur.empreinte_n2:
        return False, "N2 invalide"

    if score < 0 or score > 10:
        return False, "Score invalide"

    ## blind signature 


    blinded_msg, r = blind_message(score, public_key, hash_func)
    blinded_signature = blind_sign(blinded_msg, private_key)
    signature = unblind_signature(blinded_signature, r, public_key)

    if not verify(hash_func(score), signature, public_key):
        return False, "Signature invalide"

  ## tth 

    vote_message = f"{n2}{score}"

    while len(vote_message) % 4 != 0:
        vote_message += "A"

    fingerprint = tth.hash(vote_message)

   ## stockage dans la base de donnes 


    bulletin = Bulletin(
        vote_chiffre=str(score).encode(),
        signature=str(signature),
        code_n2=n2,
        tth_hash=fingerprint
    )

    resultat = Resultat(
        code_n2=n2,
        note=score,
        sig_valide=True,
        n2_valide=True
    )

    db.add(bulletin)
    db.add(resultat)

    electeur.a_vote = True

    db.commit()

    return True, "Vote sécurisé enregistré"

## afficher les resultats 


def show_results(db):
    print("\nVotes enregistrés :\n")

    bulletins = db.query(Bulletin).all()

    if not bulletins:
        print("Aucun vote pour le moment.")
        return

    for b in bulletins:
        score = b.vote_chiffre.decode()

        print(
            b.code_n2,
            "->", score,
            "| signature:", b.signature,
            "| TTH:", b.tth_hash
        )


##main

def main():
    db = SessionLocal()

    # Initialiser votants
    init_voters(db)

    while True:
        print("\n===== SYSTEME DE VOTE =====")
        print("1. Voter")
        print("2. Voir les résultats")
        print("3. Quitter")

        choix = input("Choix: ")

        if choix == "1":
            n1 = input("Entrer N1: ")
            n2 = input("Entrer N2: ")

            try:
                score = int(input("Entrer score (0-10): "))
            except ValueError:
                print("Score doit être un nombre")
                continue

            success, message = submit_vote(db, n1, n2, score)
            print(message)

        elif choix == "2":
            show_results(db)

        elif choix == "3":
            print("Au revoir !")
            break

        else:
            print("Choix invalide")


##Run

if __name__ == "__main__":
    main()
