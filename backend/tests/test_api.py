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

# 2. A tesztkliens
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
    assert len(spots) >= 5
    assert spots[0]["spot_type"] == SpotType.standard.value

def test_create_and_overlap_booking(client):
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

    # Sikeres foglalás tesztelése
    response1 = client.post("/api/bookings", json=booking_data)
    assert response1.status_code == 201

    # Ütközés tesztelése
    overlap_data = {
        "spot_id": spot_id,
        "requester_name": "Masik Ember",
        "start_time": (start_time + timedelta(hours=1)).isoformat(),
        "end_time": (end_time + timedelta(hours=1)).isoformat()
    }
    response2 = client.post("/api/bookings", json=overlap_data)
    assert response2.status_code == 409
    assert "már foglalt" in response2.json()["detail"]

def test_get_spot_bookings(client):
    spots_response = client.get("/api/spots")
    spot_id = spots_response.json()[0]["id"]

    now = datetime.now(timezone.utc)
    booking_data = {
        "spot_id": spot_id,
        "requester_name": "Lekerdezos Teszt Elek",
        "start_time": (now + timedelta(days=2)).isoformat(),
        "end_time": (now + timedelta(days=2, hours=1)).isoformat()
    }
    client.post("/api/bookings", json=booking_data)

    response = client.get(f"/api/spots/{spot_id}/bookings")
    assert response.status_code == 200
    
    bookings = response.json()
    assert len(bookings) >= 1
    assert any(b["requester_name"] == "Lekerdezos Teszt Elek" for b in bookings)

def test_cancel_booking(client):
    spots_response = client.get("/api/spots")
    spot_id = spots_response.json()[1]["id"] 

    now = datetime.now(timezone.utc)
    booking_data = {
        "spot_id": spot_id,
        "requester_name": "Torlos Teszt Elek",
        "start_time": (now + timedelta(days=3)).isoformat(),
        "end_time": (now + timedelta(days=3, hours=2)).isoformat()
    }
    create_response = client.post("/api/bookings", json=booking_data)
    booking_id = create_response.json()["id"]

    cancel_response = client.delete(f"/api/bookings/{booking_id}")
    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "cancelled"

    cancel_again_response = client.delete(f"/api/bookings/{booking_id}")
    assert cancel_again_response.status_code == 400
    assert "már le van mondva" in cancel_again_response.json()["detail"]