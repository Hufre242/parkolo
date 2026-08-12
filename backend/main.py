from contextlib import asynccontextmanager
from fastapi import FastAPI
from db.database import engine, SessionLocal, Base
from db.models import Spot, SpotType

# Létrehozzuk a táblákat az adatbázisban (ha még nem léteznek)
Base.metadata.create_all(bind=engine)

def seed_database():
    """Feltölti az adatbázist alapértelmezett parkolóhelyekkel, ha üres."""
    db = SessionLocal()
    try:
        # Ellenőrizzük, van-e már legalább egy parkolóhely
        if db.query(Spot).first() is None:
            spots = [
                Spot(name="A1", spot_type=SpotType.standard),
                Spot(name="A2", spot_type=SpotType.standard),
                Spot(name="A3", spot_type=SpotType.standard),
                Spot(name="B1", spot_type=SpotType.disabled),
                Spot(name="C1", spot_type=SpotType.ev_charger),
            ]
            db.add_all(spots)
            db.commit()
            print("Adatbázis inicializálva: 5 teszt parkolóhely hozzáadva.")
        else:
            print("Az adatbázis már tartalmaz adatokat, inicializálás kihagyva.")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Szerver indulásakor lefutó rész
    seed_database()
    yield
    # Szerver leállásakor lefutó rész 

from api.endpoints import router as api_router

app = FastAPI(title="Parkolóhely-foglalás API", lifespan=lifespan)

app.include_router(api_router, prefix="/api")

@app.get("/")
def root_info():
    return {
        "message": "Üdvözöllek a Parkolóhely-foglalás API-ban!",
        "instructions": "A rendszer interaktív dokumentációját és tesztelési felületét a /docs útvonalon találod.",
        "endpoints": {
            "dokumentacio": "/docs",
            "parkolohelyek_lekerdezese": "/api/spots",
            "foglalasok_lekerdezese_es_letrehozasa": "/api/bookings"
        }
    }