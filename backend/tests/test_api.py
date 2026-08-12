import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta, timezone

from main import app
from db.database import Base, get_db
from db.models import Spot, SpotType

# 1. Ideiglenes in-memory adatbázis beállítása a tesztekhez
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Függőség felülbírálása (override)
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# 2. A tesztkliens, ami meghívja a lifespan eseményt is (seeding)
@pytest.fixture(scope="module")
def client():
    # Létrehozza a sémát az üres SQLite-ban
    Base.metadata.create_all(bind=engine)

    # --- TESZT ADATBÁZIS INICIALIZÁLÁSA ---
    db = TestingSessionLocal()
    test_spots = [
        Spot(name="TestA1", spot_type=SpotType.standard),
        Spot(name="TestA2", spot_type=SpotType.standard),
        Spot(name="TestA3", spot_type=SpotType.standard),
        Spot(name="TestB1", spot_type=SpotType.disabled),
        Spot(name="TestC1", spot_type=SpotType.ev_charger),
    ]
    db.add_all(test_spots)
    db.commit()
    db.close()
    # --------------------------------------

    with TestClient(app) as c:
        yield c

    Base.metadata.drop_all(bind=engine)

# 3. Maguk a tesztek

def test_root_info(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_get_spots(client):
    response = client.get("/api/spots")
    assert response.status_code == 200
    spots = response.json()
    assert len(spots) >= 5 # A seeding miatt 5-nek lennie kell
    assert spots[0]["spot_type"] == SpotType.standard.value

def test_create_and_overlap_booking(client):
    # Lekérünk egy parkolóhelyet, amire foglalni fogunk
    spots_response = client.get("/api/spots")
    spot_id = spots_response.json()[0]["id"]

    now = datetime.now(timezone.utc)
    start_time = now + timedelta(days=1)
    end_time = start_time + timedelta(hours=2)

    booking_data = {
        "spot_id": spot_id,
        "requester_name": "Teszt Elek",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    }

    # 1. Sikeres foglalás tesztelése
    response1 = client.post("/api/bookings", json=booking_data)
    assert response1.status_code == 201
    assert response1.json()["requester_name"] == "Teszt Elek"

    # 2. Ütközés tesztelése (ugyanarra az időpontra próbálunk foglalni)
    overlap_data = {
        "spot_id": spot_id,
        "requester_name": "Másik Ember",
        "start_time": (start_time + timedelta(hours=1)).isoformat(), # Rácsúszik az előzőre
        "end_time": (end_time + timedelta(hours=1)).isoformat()
    }
    response2 = client.post("/api/bookings", json=overlap_data)
    
    # A logikánk 409-es (Conflict) hibát kell, hogy dobjon
    assert response2.status_code == 409
    assert "már foglalt" in response2.json()["detail"]