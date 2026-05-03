from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from databases.models import Base
import os

# Reads the connection URL from an environment variable (recommended for security)
DATABASE_URL = os.getenv("DATABASE_URL")
# Example format:
# postgresql://username:password@host:port/database_name
# For Supabase it looks like:
# postgresql://postgres:YOUR_PASSWORD@db.xxxxxxxxxxxx.supabase.co:5432/postgres

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL environment variable is not set.")

engine = create_engine(DATABASE_URL)
# Note: No connect_args needed for PostgreSQL (that was SQLite-specific)
# Note: The PRAGMA foreign_keys event is also removed — PostgreSQL enforces
#       foreign keys by default, so no workaround is needed.

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
