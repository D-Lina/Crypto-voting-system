from core.protocol.VotingSession import VotingSession
from core.protocol.voter import Voter
import sqlite3

# -----------------------------
# DATABASE SETUP
# -----------------------------
def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            n1 TEXT,
            vote INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def save_vote(n1, vote):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO votes (n1, vote) VALUES (?, ?)",
        (n1, vote)
    )

    conn.commit()
    conn.close()


# -----------------------------
# MAIN SYSTEM
# -----------------------------
def main():
    print("===== SECURE VOTING SYSTEM (HYBRID) =====")

    # Init database
    init_db()

    # 1. Create session
    session = VotingSession()

    # 2. Voters
    voters_data = [
        {"n1": "VOTANT001", "n2": "CODEA12345"},
        {"n1": "VOTANT002", "n2": "CODEB67890"},
        {"n1": "VOTANT003", "n2": "CODEC54321"},
        {"n1": "VOTANT004", "n2": "CODED09876"},
    ]

    # 3. Setup election
    session.setup_election(
        voters=voters_data,
        admin_primes=(61, 53),
        counter_primes=(59, 47)
    )

    # 4. Get public keys
    keys = session.get_public_keys()
    admin_key = keys["admin"]
    counter_key = keys["counter"]

    # -----------------------------
    # MENU LOOP
    # -----------------------------
    while True:
        print("\n===== MENU =====")
        print("1. Vote")
        print("2. Close voting")
        print("3. Count votes")
        print("4. Show detailed results")
        print("5. Exit")

        choice = input("Choice: ")

        # -----------------------------
        # VOTE
        # -----------------------------
        if choice == "1":
            n1 = input("Enter N1: ")
            n2 = input("Enter N2: ")

            try:
                vote = int(input("Enter vote (0-10): "))
                if vote < 0 or vote > 10:
                    raise ValueError("Vote must be between 0 and 10")
            except ValueError as e:
                print(f"❌ Invalid input: {e}")
                continue

            voter = Voter(n1, n2)

            try:
                success = voter.cast_vote(
                    vote=vote,
                    administrator=session.administrator,
                    anonymizer=session.anonymizer,
                    admin_public_key=admin_key,
                    counter_public_key=counter_key
                )

                if success:
                    save_vote(n1, vote)
                    print("✅ Vote successfully submitted and saved")
                else:
                    msg = getattr(voter, "last_error", "Vote rejected")
                    print(f"❌ {msg}")

            except Exception as e:
                print("❌ Unexpected error:", str(e))

        # -----------------------------
        # CLOSE VOTING
        # -----------------------------
        elif choice == "2":
            try:
                session.close_voting()
                print("🔒 Voting is now closed")
            except Exception as e:
                print("❌ Error:", str(e))

        # -----------------------------
        # COUNT VOTES
        # -----------------------------
        elif choice == "3":
            try:
                results = session.start_counting()
                print("\n📊 Summary:")
                print(results)
            except Exception as e:
                print("❌ Error:", str(e))

        # -----------------------------
        # DETAILED RESULTS
        # -----------------------------
        elif choice == "4":
            try:
                results = session.get_results()

                print("\n📋 Detailed Results:")
                for r in results:
                    print({
                        "code_n2": r.code_n2,
                        "vote": r.note,
                        "signature_valid": r.sig_valide,
                        "n2_valid": r.n2_valide
                    })

            except Exception as e:
                print("❌ Error:", str(e))

        # -----------------------------
        # EXIT
        # -----------------------------
        elif choice == "5":
            print("Goodbye 👋")
            break

        else:
            print("❌ Invalid choice")


if __name__ == "__main__":
    main()
