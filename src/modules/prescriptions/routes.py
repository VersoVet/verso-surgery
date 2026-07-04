"""Routes FastAPI pour les ordonnances anesthésiques."""

from typing import Any

from fastapi import APIRouter

from src.modules.prescriptions.service import PrescriptionService
from src.modules.surgeries.service import SurgeryService

router = APIRouter(prefix="/api/prescriptions", tags=["prescriptions"])


@router.post("/{surgery_id}/create-ordonnance")
async def create_anesthetic_ordonnance(
    surgery_id: str,
    animal_id: str,
    veto_id: int | None = None,
    veto_nom: str | None = None,
) -> dict[str, Any]:
    """Crée une ordonnance anesthésique dans VetoPartner via erp-connector.

    Cherche les codes centraux des médicaments et crée l'ordonnance.
    Les médicaments non trouvés sont créés comme "hors_stock".

    Args:
        surgery_id: ID de la chirurgie (avec doses calculées)
        animal_id: ID de l'animal (numérique pour VetoPartner)
        veto_id: ID du vétérinaire (optionnel)
        veto_nom: Nom du vétérinaire (optionnel)

    Returns:
        Status de création de l'ordonnance avec ID et détails.
    """
    # Récupérer la chirurgie
    surgery = SurgeryService.get_surgery(surgery_id)
    if not surgery:
        return {"error": "Surgery not found", "status": 404}

    # Créer l'ordonnance via erp-connector
    result = await PrescriptionService.create_ordonnance(
        animal_id=animal_id,
        surgery=surgery,
        veto_id=veto_id,
        veto_nom=veto_nom,
    )
    return result
