import enum
from sqlalchemy import Column, Integer, String, Enum, DateTime
from sqlalchemy.sql import func
from src.database.database import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    AGRICULTEUR = "agriculteur"
    RESPONSABLE_QUALITE = "responsable_qualite"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.AGRICULTEUR, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

from typing import Optional
from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20)) # 'supplier', 'admin', 'quality_control'
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Configuration pour l'héritage
    __mapper_args__ = {
        "polymorphic_identity": "user",
        "polymorphic_on": "role",
    }