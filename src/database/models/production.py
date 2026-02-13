import enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database.database import Base

class LotStatus(str, enum.Enum):
    RECEIVED = "received"
    PROCESSED = "processed"
    SHIPPED = "shipped"

class Lot(Base):
    __tablename__ = "lots"

    id = Column(Integer, primary_key=True, index=True)
    parcel_id = Column(Integer, ForeignKey("parcels.id"), nullable=True) # Link to origin parcel
    harvest_date = Column(DateTime, nullable=True)
    qr_code = Column(String, unique=True, index=True, nullable=False)
    quantity_kg = Column(Float, nullable=False)
    status = Column(Enum(LotStatus), default=LotStatus.RECEIVED)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    parcel = relationship("src.database.models.farms.Parcel", backref="lots")

class QualityCheck(Base):
    __tablename__ = "quality_checks"

    id = Column(Integer, primary_key=True, index=True)
    lot_id = Column(Integer, ForeignKey("lots.id"), nullable=False)
    inspector_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    defects_stats = Column(JSON, nullable=True) # e.g. {"rot": 5, "size_mismatch": 10}
    quality_score = Column(Float, nullable=True) # 0 to 100
    check_date = Column(DateTime(timezone=True), server_default=func.now())

    lot = relationship("Lot", backref="quality_checks")
    inspector = relationship("src.database.models.users.User", backref="inspections")

