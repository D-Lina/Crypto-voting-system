import sqlite3

# Connexion à la même base que ton application
conn = sqlite3.connect("database.db")
cur = conn.cursor()

# Sélectionne tout dans la table bulletins
cur.execute("SELECT * FROM bulletins")
rows = cur.fetchall()

# Affiche chaque ligne
for row in rows:
    print(row)

# Ferme la connexion
conn.close()
