from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, Boolean, func
from sqlalchemy.orm import relationship, backref
from .base import Base
from .enums import UserRole

class User(Base):
    __tablename__ = "users"

    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # --- RÔLE ET STATUT ---
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)

    # --- ARCHITECTURE DES ORGANISATIONS (Ferme ou Station) ---
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    organization = relationship("Organization", back_populates="members")

    # --- HIÉRARCHIE OPÉRATIONNELLE (Chef vs Employé) ---
    supervisor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relation pour que le chef puisse voir son équipe

    team_members = relationship(
        "User",
        backref=backref("supervisor", remote_side=[id]),
        cascade="all, delete-orphan"
    )


    # --- DONNÉES DE PROFIL (PWA) ---
    full_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    profile_image_url = Column(String(255), nullable=True)
    
   
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # --- CONFIGURATION POLYMORPHISME (Héritage) ---
    __mapper_args__ = {
        "polymorphic_on": role,
        "polymorphic_identity": "user",
    }






# --- SOUS-CLASSES POUR LA LOGIQUE MÉTIER ---

class Admin(User):
    __mapper_args__ = {"polymorphic_identity": UserRole.ADMIN}

class Agriculteur(User):
    """Gère aussi bien le propriétaire de la ferme que ses techniciens"""
    __mapper_args__ = {"polymorphic_identity": UserRole.AGRICULTEUR}

class QualityControl(User):
    """Gère le chef de station et ses contrôleurs"""
    __mapper_args__ = {"polymorphic_identity": UserRole.QUALITE}

class Consumer(User):
    """Utilisateur de l'application mobile de scan/achat"""
    __mapper_args__ = {"polymorphic_identity": UserRole.CONSOMMATEUR}