from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, Boolean, func
from sqlalchemy.orm import relationship, backref, validates
from src.database.database import Base
from src.database.models.enums import UserRole

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




    # --- DONNÉES DE PROFIL (PWA) ---
    full_name = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    

    # --- RELATIONSHIPS ---
    diagnostics = relationship("ConsumerDiagnostic", back_populates="user")

    __mapper_args__ = {
        "polymorphic_on": role,
        "polymorphic_identity": "user",
    }






# --- SOUS-CLASSES POUR LA LOGIQUE MÉTIER ---

class Admin(User):
    """Administrateur du système avec accès global"""
    __mapper_args__ = {"polymorphic_identity": UserRole.ADMIN}

class Agriculteur(User):
    """Gère aussi bien le propriétaire de la ferme que ses techniciens.
    Lié aux lots de récolte et aux diagnostics de plantes.
    """
    __mapper_args__ = {"polymorphic_identity": UserRole.AGRICULTEUR}
    
    # Relation vers les lots produits par cet agriculteur
    lots = relationship("LotRecolte", back_populates="agriculteur")

class QualityControl(User):
    """Gère le chef de station et ses contrôleurs"""
    __mapper_args__ = {"polymorphic_identity": UserRole.QUALITE}

class Consumer(User):
    """Utilisateur de l'application mobile de scan/achat.
    Conserve l'historique de ses diagnostics de fraîcheur.
    """
    __mapper_args__ = {"polymorphic_identity": UserRole.CONSOMMATEUR}
    
    # Historique des diagnostics personnels (Moved to User to avoid mapper errors)