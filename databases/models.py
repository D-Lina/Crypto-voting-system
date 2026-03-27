from sqlalchemy import (
    create_engine, Column, Text, Integer,
    Boolean, String, LargeBinary, CheckConstraint
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Electeur(Base):
    __tablename__ = 'electeurs'
    code_n1      = Column(Text, primary_key=True)
    empreinte_n2 = Column(String(4), nullable=False)
    a_vote       = Column(Boolean, default=False)


class Bulletin(Base):
    __tablename__ = 'bulletins'
    id           = Column(Integer, primary_key=True, autoincrement=True)
    vote_chiffre = Column(LargeBinary, nullable=False)
    signature    = Column(Text, nullable=False)
    code_n2      = Column(Text, nullable=False)


class Resultat(Base):
    __tablename__ = 'resultats'
    __table_args__ = (
        CheckConstraint('note BETWEEN 0 AND 10', name='check_note'),
    )
    id         = Column(Integer, primary_key=True, autoincrement=True)
    code_n2    = Column(Text, unique=True, nullable=False)
    note       = Column(Integer)
    sig_valide = Column(Boolean, nullable=False)
    n2_valide  = Column(Boolean, nullable=False)


class User(Base):
    __tablename__ = 'users'
    __table_args__ = (
        CheckConstraint("role IN ('commissaire', 'admin', 'electeur', 'decompte')", name='check_role'),
    )
    id            = Column(Integer, primary_key=True, autoincrement=True)
    username      = Column(Text, unique=True)
    password_hash = Column(Text, nullable=False)
    role          = Column(Text, nullable=False)


class CleRSA(Base):
    __tablename__ = 'cles_rsa'
    __table_args__ = (
        CheckConstraint("entite IN ('admin', 'decompte')", name='check_entite'),
    )
    id           = Column(Integer, primary_key=True, autoincrement=True)
    entite       = Column(Text, unique=True)
    cle_publique = Column(Text, nullable=False)
    cle_privee   = Column(Text, nullable=False)
