"""Routes FastAPI pour le suivi de prise en charge."""

from typing import Any

from fastapi import APIRouter, HTTPException

from src.models import (
    ActesRequest,
    AnesthesieRequest,
    ArriveRequest,
    SortieRequest,
)
from src.modules.suivi.service import (
    get_preview,
    load_suivi_protocols,
    process_actes,
    process_anesthesie,
    process_arrivee,
    process_sortie,
)
from src.modules.suivi.store import delete_tracking, list_today_trackings, load_tracking

router = APIRouter(prefix="/api/suivi", tags=["suivi"])


@router.get("/protocoles")
async def get_protocoles() -> dict[str, Any]:
    """Récupère les protocoles anesthésiques pour suivi.

    Returns:
        Dict avec liste des protocoles.
    """
    protocoles = load_suivi_protocols()
    return {"protocoles": [p.model_dump() for p in protocoles]}


@router.get("/tracking")
async def get_all_trackings(date: str | None = None) -> dict[str, Any]:
    """Récupère les trackings du jour.

    Args:
        date: Date au format YYYY-MM-DD (défaut: aujourd'hui).

    Returns:
        Dict avec liste des trackings.
    """
    from datetime import date as date_module

    if not date:
        date = date_module.today().isoformat()

    trackings = list_today_trackings(date)
    return {"trackings": [t.model_dump() for t in trackings], "date": date}


@router.get("/tracking/{appointment_id}")
async def get_tracking(appointment_id: str) -> dict[str, Any]:
    """Récupère le tracking d'un rendez-vous.

    Args:
        appointment_id: ID du rendez-vous.

    Returns:
        Dict avec tracking ou erreur.
    """
    tracking = load_tracking(appointment_id)
    if not tracking:
        raise HTTPException(status_code=404, detail="Tracking not found")

    return {"success": True, "tracking": tracking.model_dump()}


@router.delete("/tracking/{appointment_id}")
async def reset_tracking(appointment_id: str) -> dict[str, Any]:
    """Réinitialise le tracking d'un rendez-vous.

    Args:
        appointment_id: ID du rendez-vous.

    Returns:
        Dict avec succès.
    """
    success = delete_tracking(appointment_id)
    return {"success": success, "appointment_id": appointment_id}


@router.post("/arrivee")
async def handle_arrivee(request: ArriveRequest) -> dict[str, Any]:
    """Traite l'arrivée du patient — étape 1.

    Args:
        request: Données d'arrivée.

    Returns:
        Dict avec succès et tracking.
    """
    try:
        tracking = await process_arrivee(request)
        return {"success": True, "tracking": tracking.model_dump()}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/anesthesie")
async def handle_anesthesie(request: AnesthesieRequest) -> dict[str, Any]:
    """Traite l'anesthésie — étape 2 avec ordonnance.

    Args:
        request: Données d'anesthésie.

    Returns:
        Dict avec succès, tracking, ordonnance_id.
    """
    try:
        result = await process_anesthesie(request)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/actes")
async def handle_actes(request: ActesRequest) -> dict[str, Any]:
    """Traite les actes/soins — étape 3.

    Args:
        request: Données des actes.

    Returns:
        Dict avec succès et tracking.
    """
    try:
        tracking = await process_actes(request)
        return {"success": True, "tracking": tracking.model_dump()}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/sortie")
async def handle_sortie(request: SortieRequest) -> dict[str, Any]:
    """Traite la sortie — étape 4 avec consultation VetoPartner.

    Args:
        request: Données de sortie.

    Returns:
        Dict avec succès, tracking, consultation_id.
    """
    try:
        result = await process_sortie(request)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/preview/{appointment_id}")
async def get_consultation_preview(appointment_id: str) -> dict[str, Any]:
    """Prévisualise le compte-rendu avant validation.

    Args:
        appointment_id: ID du rendez-vous.

    Returns:
        Dict avec aperçu du CR.
    """
    preview = get_preview(appointment_id)
    return {"success": True, "preview": preview}
