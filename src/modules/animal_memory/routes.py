"""Routes API pour mémoire des traitements par animal."""

from typing import Any

from fastapi import APIRouter

from src.modules.animal_memory.service import get_last_session

router = APIRouter(prefix="/api/animal-memory", tags=["animal-memory"])


@router.get("/{animal_id}/last-session")
async def get_last_session_route(
    animal_id: int,
    act_id: str,
) -> dict[str, Any]:
    """Récupère la dernière séance d'un acte pour un animal.

    Args:
        animal_id: ID VetoPartner de l'animal (path).
        act_id: ID de l'acte (query).

    Returns:
        Dict avec found bool et session data si trouvée.

    Example:
        GET /api/animal-memory/21892/last-session?act_id=onde_de_choc
        → {"found": false}
        ou
        → {"found": true, "session": {"date": "2026-07-01", "num_seance": 1, ...}}
    """
    session = await get_last_session(animal_id, act_id)
    if session is None:
        return {"found": False}
    return {"found": True, "session": session}
