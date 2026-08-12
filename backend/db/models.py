from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from database import Base

# Az extra feladat miatti típusok (pl. normál, mozgáskorlátozott, elektromos töltő)
class SpotType(str, enum.Enum):
    standard = "standard"
    disabled = "disabled"
    ev_charger = "ev_charger"

# Foglalás státuszok - így a lemondáskor nem törlünk, csak státuszt váltunk
class BookingStatus(str, enum.Enum):
    active = "active"
    cancelled = "cancelled"

class Spot(Base):
    __tablename__ = "spots"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    spot_type = Column(Enum(SpotType), default=SpotType.standard, nullable=False)

    # Kapcsolat a foglalások felé
    bookings = relationship("Booking", back_populates="spot")

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    spot_id = Column(Integer, ForeignKey("spots.id"), nullable=False)
    requester_name = Column(String, nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.active, nullable=False)

    # Visszautalás a parkolóhelyre
    spot = relationship("Spot", back_populates="bookings")