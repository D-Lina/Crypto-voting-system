from sqlalchemy import (
    Column, Text, Integer,
    Boolean, String, LargeBinary, CheckConstraint
)
from sqlalchemy.orm import declarative_base
Base = declarative_base()

# Registre électoral : qui a le droit de voter et qui a déjà voté
class Electeur(Base):
    __tablename__ = 'electeurs'
    code_n1      = Column(Text, primary_key=True)  # identifiant unique du votant
    empreinte_n2 = Column(String(4), nullable=False) # hash TTH du code N2
    a_vote       = Column(Boolean, default=False)   # anti-double vote

# Urne électorale : stocke les votes chiffrés de façon anonyme (sans N1)
class Bulletin(Base):
    __tablename__ = 'bulletins'
    id           = Column(Integer, primary_key=True, autoincrement=True)
    vote_chiffre = Column(LargeBinary, nullable=False)    # vote chiffré RSA (binaire)
    signature    = Column(Text, nullable=False) # signature aveugle de l'admin
    code_n2      = Column(Text, nullable=False)  # pour vérification finale

# Procès-verbal : stocke les votes déchiffrés et vérifiés après dépouillement
class Resultat(Base):
    __tablename__ = 'resultats'
    __table_args__ = (
        CheckConstraint('note BETWEEN 0 AND 10', name='check_note'),
    )
    id         = Column(Integer, primary_key=True, autoincrement=True)
    code_n2    = Column(Text, unique=True, nullable=False)  # lien vers le bulletin
    note       = Column(Integer)      # vote déchiffré (0 à 10)
    sig_valide = Column(Boolean, nullable=False)             # signature admin vérifiée ?
    n2_valide  = Column(Boolean, nullable=False)  # code N2 vérifié ?

# Comptes système : authentifie les 4 acteurs du protocole (admin, commissaire, electeur, decompte)
class User(Base):
    __tablename__ = 'users'
    __table_args__ = (
        CheckConstraint("role IN ('commissaire', 'admin', 'electeur', 'decompte')", name='check_role'),
    )
    id            = Column(Integer, primary_key=True, autoincrement=True)
    username      = Column(Text, unique=True)
    password_hash = Column(Text, nullable=False)   # SHA-256, jamais en clair
    role          = Column(Text, nullable=False) # 'commissaire' | 'admin' | 'electeur' | 'decompte'

# Coffre-fort : stocke les 2 paires de clés RSA pour signer et chiffrer les votes
class CleRSA(Base):
    __tablename__ = 'cles_rsa'
    __table_args__ = (
        CheckConstraint("entite IN ('admin', 'decompte')", name='check_entite'),
    )
    id           = Column(Integer, primary_key=True, autoincrement=True)
    entite       = Column(Text, unique=True)  # 'admin' ou 'decompte'
    cle_publique = Column(Text, nullable=False)   # clé publique RSA (format PEM)
    cle_privee   = Column(Text, nullable=False)  # clé privée RSA (format PEM)
