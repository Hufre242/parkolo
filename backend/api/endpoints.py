from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from db.models import Spot, Booking, BookingStatus
from schemas.schemas import Spot as SpotSchema, Booking as BookingSchema, BookingCreate

router = APIRouter()

# 1. Parkolóhelyek lekérdezése
@router.get("/spots", response_model=List[SpotSchema])
def get_spots(db: Session = Depends(get_db)):
    return db.query(Spot).all()

# 2. Egy adott parkolóhely foglalásainak lekérdezése
@router.get("/spots/{spot_id}/bookings", response_model=List[BookingSchema])
def get_spot_bookings(spot_id: int, db: Session = Depends(get_db)):
    spot = db.query(Spot).filter(Spot.id == spot_id).first()
    if not spot:
        raise HTTPException(status_code=404, detail="Parkolóhely nem található")
    
    return db.query(Booking).filter(Booking.spot_id == spot_id).all()

# 3. Foglalás lemondása ("Soft delete" státuszváltással)
@router.delete("/bookings/{booking_id}", response_model=BookingSchema)
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Foglalás nem található")
    
    if booking.status == BookingStatus.cancelled:
        raise HTTPException(status_code=400, detail="A foglalás már le van mondva")
        
    booking.status = BookingStatus.cancelled
    db.commit()
    db.refresh(booking)
    return booking

# 4. Foglalási kérés leadása és validálása
@router.post("/bookings", response_model=BookingSchema, status_code=status.HTTP_201_CREATED)
def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    # 4.a Alapvető logikai validáció
    if booking.start_time >= booking.end_time:
        raise HTTPException(status_code=400, detail="A kezdő időpontnak korábbinak kell lennie a záró időpontnál")
        
    spot = db.query(Spot).filter(Spot.id == booking.spot_id).first()
    if not spot:
        raise HTTPException(status_code=404, detail="Parkolóhely nem található")

    # 4.b ÜTKÖZÉSVIZSGÁLAT (Adatbázis szinten optimalizálva)
    # Két időintervallum (A és B) akkor ütközik, ha: A.kezdet < B.vég ÉS A.vég > B.kezdet
    overlapping_booking = db.query(Booking).filter(
        Booking.spot_id == booking.spot_id,
        Booking.status == BookingStatus.active, # Csak az aktív foglalásokat nézzük
        Booking.start_time < booking.end_time,
        Booking.end_time > booking.start_time
    ).first()

    if overlapping_booking:
        raise HTTPException(status_code=409, detail="A választott időpontban a parkolóhely már foglalt")

    # 4.c Foglalás mentése
    new_booking = Booking(
        spot_id=booking.spot_id,
        requester_name=booking.requester_name,
        start_time=booking.start_time,
        end_time=booking.end_time,
        status=BookingStatus.active
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    
    return new_booking