import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# A docker-compose.yml-ben definiált DATABASE_URL-t használjuk
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://admin:adminpassword@localhost:5433/parking_db"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Adatbázis session függőség a FastAPI végpontokhoz
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()