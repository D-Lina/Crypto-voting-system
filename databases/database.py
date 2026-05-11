from dotenv import load_dotenv
load_dotenv()  # charge les variables depuis le fichier .env
 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from databases.models import Base  # importe les modèles pour créer les tables
import os
 
# récupère l'adresse de connexion à la base de données
DATABASE_URL = os.getenv("DATABASE_URL")
 
# si l'adresse est absente, on arrête tout de suite
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL environment variable is not set.")
 
# crée la connexion à la base de données
engine = create_engine(DATABASE_URL)
 
# crée une fabrique de sessions (les changements doivent être confirmés manuellement)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
 
def get_db():
    db = SessionLocal()  # ouvre une session pour chaque requête
    try:
        yield db  # donne la session à l'endpoint qui en a besoin
    finally:
        db.close()  # ferme toujours la session à la fin, même en cas d'erreur
 
def init_db():
    Base.metadata.drop_all(bind=engine)   # supprime toutes les tables
    Base.metadata.create_all(bind=engine) # recrée toutes les tables depuis models.py
 
