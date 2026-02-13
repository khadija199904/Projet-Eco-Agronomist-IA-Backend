from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database.database import Base

class Diagnostic(Base):
    __tablename__ = "diagnostics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parcel_id = Column(Integer, ForeignKey("parcels.id"), nullable=True)
    image_url = Column(String, nullable=True)
    prediction_result = Column(JSON, nullable=True) # Store JSON result from AI
    confidence_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("src.database.models.users.User", backref="diagnostics")
    parcel = relationship("src.database.models.farms.Parcel", backref="diagnostics")

class Treatment(Base):
    __tablename__ = "treatments"

    id = Column(Integer, primary_key=True, index=True)
    diagnostic_id = Column(Integer, ForeignKey("diagnostics.id"), nullable=False)
    product_used = Column(String, nullable=False)
    dosage = Column(String, nullable=False)
    application_date = Column(DateTime(timezone=True), server_default=func.now())
    dar_days = Column(Integer, nullable=True) # Delai Avant Recolte in days

    diagnostic = relationship("Diagnostic", backref="treatments")
