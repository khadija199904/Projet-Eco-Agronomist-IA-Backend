import enum

# Sécuriser les types de rôles et d'organisations.
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    AGRICULTEUR = "agriculteur"
    QUALITE = "responsable_qualite"
    CONSOMMATEUR = "consommateur"

class OrgType(str, enum.Enum):
    FERME = "ferme"
    STATION = "station_conditionnement"