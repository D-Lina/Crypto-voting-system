from core.protocol.VotingSession import VotingSession
from core.protocol.voter import Voter


def main():
    print("===== SECURE VOTING SYSTEM =====")

    # 1. Create a voting session (this initializes all entities internally)
    session = VotingSession()

    # 2. Define voters (N1 = identity code, N2 = secret verification code)
    voters_data = [
        {"n1": "VOTANT001", "n2": "CODEA12345"},
        {"n1": "VOTANT002", "n2": "CODEB67890"},
        {"n1": "VOTANT003", "n2": "CODEC54321"},
        {"n1": "VOTANT004", "n2": "CODED09876"},
        {"n1": "VOTANT005", "n2": "CODEE11223"},
    ]

    # 3. Setup the election
    # - Commissioner stores voters in DB
    # - Administrator generates RSA keys
    # - Counter generates its own RSA keys
    # - Anonymizer is initialized
    session.setup_election(
        voters=voters_data,
        admin_primes=(61, 53),
        counter_primes=(59, 47)
    )

    # 4. Retrieve public keys needed by voters
    keys = session.get_public_keys()
    admin_key = keys["admin"]
    counter_key = keys["counter"]

    # 5. Simple CLI menu
    while True:
        print("\n===== MENU =====")
        print("1. Vote")
        print("2. Close voting")
        print("3. Count votes")
        print("4. Show results")
        print("5. Exit")

        choice = input("Choice: ")

        # 🗳️ Voting process
        if choice == "1":
            n1 = input("Enter N1: ")
            n2 = input("Enter N2: ")

            try:
                vote = int(input("Enter vote (0-10): "))
            except ValueError:
                print("Invalid vote (must be a number)")
                continue

            try:
                # Create a voter instance (client-side simulation)
                voter = Voter(n1, n2)

                # Execute full voting protocol:
                # 1. Set vote
                # 2. Blind vote
                # 3. Request signature from administrator
                # 4. Unblind signature
                # 5. Encrypt vote for counter
                # 6. Submit ballot to anonymizer
                success = voter.cast_vote(
                    vote=vote,
                    administrator=session.administrator,
                    anonymizer=session.anonymizer,
                    admin_public_key=admin_key,
                    counter_public_key=counter_key
                )

                if success:
                    print("✅ Vote successfully submitted")
                else:
                    print("❌ Vote rejected")

            except Exception as e:
                print("Error:", str(e))

        # 🔒 Close voting phase
        elif choice == "2":
            try:
                session.close_voting()
                print("🔒 Voting is now closed")
            except Exception as e:
                print("Error:", str(e))

        # 🧮 Count votes
        elif choice == "3":
            try:
                results = session.start_counting()
                print("\n📊 Summary:")
                print(results)
            except Exception as e:
                print("Error:", str(e))

        # 📄 Show detailed results
        elif choice == "4":
            try:
                results = session.get_results()
                print("\n📋 Detailed Results:")

                for r in results:
                    print({
                        "code_n2": r.code_n2,
                        "note": r.note,
                        "signature_valid": r.sig_valide,
                        "n2_valid": r.n2_valide
                    })

            except Exception as e:
                print("Error:", str(e))

        # 🚪 Exit program
        elif choice == "5":
            print("Goodbye 👋")
            break

        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()
