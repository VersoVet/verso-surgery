"""Routes FastAPI pour les chirurgies."""

from typing import Any

from fastapi import APIRouter

from src.modules.surgeries.service import SurgeryService

router = APIRouter(prefix="/api/surgeries", tags=["surgeries"])


@router.post("/")
async def create_surgery(
    surgery_id: str,
    animal_id: str,
    protocol_id: str,
    weight_kg: float,
    vet_id: str = "",
) -> dict[str, Any]:
    """Crée une nouvelle chirurgie avec calcul automatique des doses.

    Args:
        surgery_id: ID unique de la chirurgie
        animal_id: ID de l'animal
        protocol_id: ID du protocole anesthésique
        weight_kg: Poids de l'animal en kg
        vet_id: ID du vétérinaire (optionnel)

    Returns:
        Les données de la chirurgie ou erreur.
    """
    surgery = SurgeryService.create_surgery(surgery_id, animal_id, protocol_id, weight_kg, vet_id)
    if not surgery:
        return {"error": "Protocol not found", "status": 404}
    return surgery.model_dump()


@router.get("/{surgery_id}")
async def get_surgery(surgery_id: str) -> dict[str, Any]:
    """Récupère une chirurgie par ID.

    Args:
        surgery_id: ID de la chirurgie

    Returns:
        Données de la chirurgie ou erreur 404.
    """
    surgery = SurgeryService.get_surgery(surgery_id)
    if not surgery:
        return {"error": "Surgery not found", "status": 404}
    return surgery.model_dump()


@router.get("/")
async def list_surgeries(animal_id: str | None = None) -> list[dict[str, Any]]:
    """Liste les chirurgies, optionnellement filtrées par animal.

    Args:
        animal_id: ID de l'animal (optionnel)

    Returns:
        Liste des chirurgies.
    """
    surgeries = SurgeryService.list_surgeries(animal_id)
    return [s.model_dump() for s in surgeries]


@router.post("/{surgery_id}/validate")
async def validate_surgery(surgery_id: str) -> dict[str, Any]:
    """Valide une chirurgie.

    Args:
        surgery_id: ID de la chirurgie

    Returns:
        Status de validation.
    """
    validated = SurgeryService.validate_surgery(surgery_id)
    if not validated:
        return {"error": "Surgery not found", "status": 404}
    return {"validated": True, "surgery_id": surgery_id}


@router.put("/{surgery_id}/notes")
async def update_surgery_notes(surgery_id: str, notes: str) -> dict[str, Any]:
    """Met à jour les notes d'une chirurgie.

    Args:
        surgery_id: ID de la chirurgie
        notes: Nouvelles notes

    Returns:
        Chirurgie mise à jour ou erreur 404.
    """
    surgery = SurgeryService.update_surgery_notes(surgery_id, notes)
    if not surgery:
        return {"error": "Surgery not found", "status": 404}
    return surgery.model_dump()
