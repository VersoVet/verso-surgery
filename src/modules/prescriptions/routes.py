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
    """Crée une ordonnance anesthésique via erp-connector pour une chirurgie.

    Valide d'abord que tous les médicaments sont disponibles en stock.

    Args:
        surgery_id: ID de la chirurgie (avec doses calculées)
        animal_id: ID de l'animal (doit être numérique pour VetoPartner)
        veto_id: ID du vétérinaire (optionnel)
        veto_nom: Nom du vétérinaire (optionnel)

    Returns:
        Status de création de l'ordonnance avec validation du stock.
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


@router.post("/{surgery_id}/validate-stock")
async def validate_anesthetic_stock(surgery_id: str) -> dict[str, Any]:
    """Valide que tous les médicaments d'une ordonnance anesthésique sont en stock.

    Utile pour vérifier la disponibilité avant de créer l'ordonnance.

    Args:
        surgery_id: ID de la chirurgie

    Returns:
        Status de validation avec détails des médicaments manquants.
    """
    surgery = SurgeryService.get_surgery(surgery_id)
    if not surgery:
        return {"error": "Surgery not found", "status": 404}

    valid, message = await PrescriptionService.validate_anesthetic_prescription(surgery)

    return {
        "valid": valid,
        "message": message,
        "surgery_id": surgery_id,
        "protocol_id": surgery.protocol_id,
        "medicines_count": len(surgery.doses),
    }
