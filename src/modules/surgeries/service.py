"""Service de gestion des chirurgies."""

from src.models import Surgery, SurgeryDose
from src.modules.protocols.service import ProtocolService

# Store en mémoire (remplacer par DB en production)
_surgeries_db: dict[str, Surgery] = {}


class SurgeryService:
    """Service pour gérer les chirurgies."""

    @staticmethod
    def create_surgery(
        surgery_id: str,
        animal_id: str,
        protocol_id: str,
        weight_kg: float,
        vet_id: str = "",
    ) -> Surgery | None:
        """Crée une nouvelle chirurgie avec calcul de doses.

        Args:
            surgery_id: ID unique de la chirurgie
            animal_id: ID de l'animal
            protocol_id: ID du protocole anesthésique
            weight_kg: Poids de l'animal
            vet_id: ID du vétérinaire (optionnel)

        Returns:
            La chirurgie créée avec doses calculées, ou None si protocole invalide.
        """
        doses_data = ProtocolService.calculate_dose(protocol_id, weight_kg)
        if not doses_data:
            return None

        doses = [SurgeryDose(**d) for d in doses_data["doses"]]

        surgery = Surgery(
            id=surgery_id,
            animal_id=animal_id,
            protocol_id=protocol_id,
            weight_kg=weight_kg,
            doses=doses,
            vet_id=vet_id,
            status="draft",
        )
        _surgeries_db[surgery_id] = surgery
        return surgery

    @staticmethod
    def get_surgery(surgery_id: str) -> Surgery | None:
        """Récupère une chirurgie par ID.

        Args:
            surgery_id: ID de la chirurgie

        Returns:
            La chirurgie ou None.
        """
        return _surgeries_db.get(surgery_id)

    @staticmethod
    def list_surgeries(animal_id: str | None = None) -> list[Surgery]:
        """Liste les chirurgies, optionnellement filtrées par animal.

        Args:
            animal_id: ID de l'animal (optionnel)

        Returns:
            Liste des chirurgies.
        """
        surgeries = _surgeries_db.values()
        if animal_id:
            return [s for s in surgeries if s.animal_id == animal_id]
        return list(surgeries)

    @staticmethod
    def validate_surgery(surgery_id: str) -> bool:
        """Valide une chirurgie (change status à 'validated').

        Args:
            surgery_id: ID de la chirurgie

        Returns:
            True si validée, False si non trouvée.
        """
        surgery = _surgeries_db.get(surgery_id)
        if not surgery:
            return False
        surgery.status = "validated"
        return True

    @staticmethod
    def update_surgery_notes(surgery_id: str, notes: str) -> Surgery | None:
        """Met à jour les notes d'une chirurgie.

        Args:
            surgery_id: ID de la chirurgie
            notes: Nouvelles notes

        Returns:
            La chirurgie mise à jour ou None.
        """
        surgery = _surgeries_db.get(surgery_id)
        if not surgery:
            return None
        surgery.notes = notes
        return surgery
