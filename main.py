from voting.votingsession import VotingSession
from voting.voter import Voter
import sqlite3

# -----------------------------
# Fonction pour sauvegarder le vote
# -----------------------------
def save_vote(n1, vote):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    # Crée la table si elle n'existe pas
    cur.execute("""
        CREATE TABLE IF NOT EXISTS votes (
            n1 TEXT PRIMARY KEY,
            vote INTEGER
        )
    """)
    # INSERT OR IGNORE pour éviter doublons
    cur.execute("INSERT OR IGNORE INTO votes (n1, vote) VALUES (?, ?)", (n1, vote))
    conn.commit()
    conn.close()

# -----------------------------
# Vérifie si le votant a déjà voté
# -----------------------------
def has_already_voted(n1):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM votes WHERE n1 = ?", (n1,))
    result = cur.fetchone()
    conn.close()
    return result is not None

# -----------------------------
# Programme principal
# -----------------------------
def main():
    # 1. Créer session
    session = VotingSession()

    # 2. Initialiser votants
    voters_data = [
        {"n1": "VOTANT001", "n2": "CODEA12345"},
        {"n1": "VOTANT002", "n2": "CODEB67890"},
        {"n1": "VOTANT003", "n2": "CODEC54321"},
    ]

    # 3. Setup élection
    session.setup_election(
        voters=voters_data,
        admin_primes=(61, 53),
        counter_primes=(59, 47)
    )

    # 4. Récupérer clés publiques
    keys = session.get_public_keys()
    if not keys or "admin" not in keys or "counter" not in keys:
        print("Erreur : les clés publiques n'ont pas été initialisées correctement")
        return

    admin_pk = keys["admin"]
    counter_pk = keys["counter"]

    while True:
        print("\n===== SYSTEME DE VOTE =====")
        print("1. Voter")
        print("2. Clôturer le vote")
        print("3. Voir résultats")
        print("4. Quitter")

        choix = input("Choix: ")

        if choix == "1":
            n1 = input("Entrer N1: ")
            n2 = input("Entrer N2: ")
            vote_input = input("Entrer score (0-10): ")

            # Vérifier si le votant a déjà voté
            if has_already_voted(n1):
                print("Vous avez déjà voté ❌")
                continue

            # Valider le vote
            try:
                vote = int(vote_input)
                if vote < 0 or vote > 10:
                    print("Vote invalide ❌ — doit être entre 0 et 10")
                    continue
            except ValueError:
                print("Vote invalide ❌ — doit être un entier")
                continue

            # Créer l'objet Voter
            voter = Voter(n1, n2)

            try:
                # Effectuer le vote
                success = voter.cast_vote(
                    vote=vote,
                    administrator=session.administrator,
                    anonymizer=session.anonymizer,
                    admin_public_key=admin_pk,
                    counter_public_key=counter_pk
                )

                if success:
                    save_vote(n1, vote)
                    print("Vote accepté ✅")
                else:
                    msg = getattr(voter, "last_error", "Vote refusé ❌")
                    print(f"Vote refusé ❌ — {msg}")

            except Exception as e:
                print("Erreur inattendue:", e)

        elif choix == "2":
            session.close_voting()
            print("Vote fermé 🔒")

        elif choix == "3":
            try:
                results = session.start_counting()
                print("\nRésultats:", results)

                details = session.get_results()
                print("\nDétails:")
                for r in details:
                    print(r)

            except Exception as e:
                print("Erreur inattendue:", e)

        elif choix == "4":
            break

        else:
            print("Choix invalide ❌")


if __name__ == "__main__":
    main()
