"""Routes FastAPI pour les protocoles anesthésiques."""

from typing import Any

from fastapi import APIRouter

from src.models import Protocol
from src.modules.protocols.service import ProtocolService

router = APIRouter(prefix="/api/protocols", tags=["protocols"])


@router.get("/")
async def list_protocols() -> list[Protocol]:
    """Liste tous les protocoles anesthésiques disponibles."""
    return ProtocolService.load_protocols()


@router.get("/{protocol_id}")
async def get_protocol(protocol_id: str) -> dict[str, Any]:
    """Récupère un protocole par ID.

    Args:
        protocol_id: ID du protocole (ex: mk_standard)

    Returns:
        Protocole avec détails ou 404.
    """
    protocol = ProtocolService.get_protocol(protocol_id)
    if not protocol:
        return {"error": "Protocol not found", "status": 404}
    return protocol.model_dump()


@router.get("/species/{species}")
async def get_protocols_by_species(species: str) -> list[Protocol]:
    """Liste les protocoles pour une espèce.

    Args:
        species: chien ou chat

    Returns:
        Protocoles disponibles pour cette espèce.
    """
    return ProtocolService.get_protocols_for_species(species)


@router.post("/doses/{protocol_id}")
async def calculate_protocol_doses(protocol_id: str, weight_kg: float) -> dict[str, Any]:
    """Calcule les doses pour un protocole et poids.

    Args:
        protocol_id: ID du protocole
        weight_kg: Poids de l'animal en kg

    Returns:
        Doses calculées pour chaque drogue.
    """
    result = ProtocolService.calculate_dose(protocol_id, weight_kg)
    if not result:
        return {"error": "Protocol not found", "status": 404}
    return result
