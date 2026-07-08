"""Routes FastAPI pour le dashboard surgical."""

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter

from src.models import CreateConsultationRequest, CreateOrdonnanceRequest
from src.modules.dashboard.service import DashboardService

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def load_acts() -> list[dict[str, Any]]:
    """Charge les actes chirurgicaux depuis acts.json.

    Returns:
        Liste des actes disponibles.
    """
    acts_file = Path(__file__).parent.parent.parent.parent / "acts.json"
    try:
        with open(acts_file) as f:
            data: Any = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


@router.get("/sites")
async def get_sites() -> dict[str, Any]:
    """Récupère tous les sites vétérinaires.

    Returns:
        Dict avec liste des sites.
    """
    return await DashboardService.get_sites()


@router.get("/vets")
async def get_vets() -> dict[str, Any]:
    """Récupère tous les vétérinaires.

    Returns:
        Dict avec liste des vétérinaires.
    """
    return await DashboardService.get_vets()


@router.get("/appointments")
async def get_appointments(
    date_from: str,
    date_to: str,
    vet_id: int | None = None,
    site_id: int | None = None,
) -> dict[str, Any]:
    """Récupère les RDV pour une plage de dates.

    Args:
        date_from: Date de début (YYYY-MM-DD)
        date_to: Date de fin (YYYY-MM-DD)
        vet_id: ID vétérinaire optionnel
        site_id: ID site optionnel

    Returns:
        Dict avec liste des RDV.
    """
    return await DashboardService.get_appointments(date_from, date_to, vet_id, site_id)


@router.get("/rdv-today")
async def get_rdv_today() -> dict[str, Any]:
    """Récupère les rendez-vous du jour.

    Returns:
        Dict avec liste des RDV ou erreur.
    """
    rdv_list = await DashboardService.get_rdv_today()
    return {"rdv": rdv_list}


@router.get("/search")
async def search_patient(q: str) -> dict[str, Any]:
    """Recherche un patient.

    Args:
        q: Terme de recherche

    Returns:
        Dict avec résultats de recherche.
    """
    if not q or len(q) < 2:
        return {"results": []}

    results = await DashboardService.search_patient(q)
    return {"results": results}


@router.get("/animal/{animal_id}")
async def get_animal(animal_id: int) -> dict[str, Any]:
    """Récupère les détails d'un animal.

    Args:
        animal_id: ID VetoPartner de l'animal

    Returns:
        Dict avec infos animal ou erreur.
    """
    animal = await DashboardService.get_animal(animal_id)
    if not animal:
        return {"error": "Animal not found", "status": 404}

    return animal


@router.get("/acts")
async def get_acts() -> dict[str, Any]:
    """Récupère la liste des actes chirurgicaux.

    Returns:
        Dict avec liste des actes.
    """
    acts = load_acts()
    return {"acts": acts}


@router.post("/consultation")
async def create_consultation(
    request: CreateConsultationRequest,
) -> dict[str, Any]:
    """Crée une consultation VetoPartner.

    Args:
        request: Données de la consultation

    Returns:
        Status de création avec ID consultation.
    """
    result = await DashboardService.create_consultation(
        animal_id=request.animal_id,
        synthese=request.synthese,
        motif=request.motif,
        veto_id=request.veto_id,
        site_id=request.site_id,
    )
    return result


@router.post("/ordonnance")
async def create_ordonnance(
    request: CreateOrdonnanceRequest,
) -> dict[str, Any]:
    """Crée une ordonnance VetoPartner.

    Args:
        request: Données de l'ordonnance

    Returns:
        Status de création avec ID ordonnance.
    """
    lignes = [ligne.model_dump() for ligne in request.lignes]
    result = await DashboardService.create_ordonnance(
        animal_id=request.animal_id,
        lignes=lignes,
        veto_id=request.veto_id,
        site_id=request.site_id,
    )
    return result
