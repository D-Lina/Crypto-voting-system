# Il sert uniquement à lancer la création manuelle des tables depuis le terminal :
from databases.database import init_db  # importe la fonction qui crée les tables

# s'exécute uniquement si on lance ce fichier directement : python db.py
if __name__ == "__main__":
    init_db()  # supprime et recrée toutes les tables de la base de données
    print(" Database created successfully!")
