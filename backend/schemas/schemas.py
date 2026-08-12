from pydantic import BaseModel, ConfigDict
from datetime import datetime
from db.models import SpotType, BookingStatus

# --- Parkolóhely (Spot) Sémák ---

class SpotBase(BaseModel):
    name: str
    spot_type: SpotType

class Spot(SpotBase):
    id: int

    # Ez mondja meg a Pydantic-nak, hogy tudja olvasni a SQLAlchemy modelleket
    model_config = ConfigDict(from_attributes=True)

# --- Foglalás (Booking) Sémák ---

class BookingBase(BaseModel):
    requester_name: str
    start_time: datetime
    end_time: datetime

class BookingCreate(BookingBase):
    spot_id: int

class Booking(BookingBase):
    id: int
    spot_id: int
    status: BookingStatus

    model_config = ConfigDict(from_attributes=True)