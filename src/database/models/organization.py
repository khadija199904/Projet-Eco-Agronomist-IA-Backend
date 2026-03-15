from sqlalchemy import Column, Integer, String, Enum, Boolean
from sqlalchemy.orm import relationship
from src.database.database import Base
from .enums import OrgType

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    type = Column(Enum(OrgType), nullable=False)
    address = Column(String(255))
    is_certified = Column(Boolean, default=False)
    
    # Lien vers les employés (Agriculteurs ou Contrôleurs)
    members = relationship("User", back_populates="organization")