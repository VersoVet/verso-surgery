"""Routes FastAPI pour le dashboard surgical."""

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Body

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


def load_presets() -> dict[str, Any]:
    """Charge les presets de zones depuis presets.json.

    Returns:
        Dict avec les presets par act_id.
    """
    presets_file = Path(__file__).parent.parent.parent.parent / "presets.json"
    try:
        with open(presets_file) as f:
            data: Any = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


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


@router.get("/presets")
async def get_presets(act_id: str | None = None) -> dict[str, Any]:
    """Récupère les presets de zones pour un acte.

    Args:
        act_id: Identifiant de l'acte (optionnel).

    Returns:
        Dict avec presets filtrés ou complets.
    """
    all_presets = load_presets()
    if act_id:
        return {"presets": all_presets.get(act_id, [])}
    return {"presets": all_presets}


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


@router.get("/config/{config_name}")
async def get_config(config_name: str) -> dict[str, Any]:
    """Récupère le contenu d'un fichier de configuration JSON.

    Args:
        config_name: Nom du fichier (acts, protocols, protocoles_suivi, presets)

    Returns:
        Contenu du fichier JSON ou erreur.
    """
    allowed_files = {"acts", "protocols", "protocoles_suivi", "presets"}
    if config_name not in allowed_files:
        return {"error": "Configuration invalide", "status": 400}

    config_file = Path(__file__).parent.parent.parent.parent / f"{config_name}.json"
    try:
        with open(config_file) as f:
            data = json.load(f)
        return {"success": True, "config": config_name, "data": data}
    except FileNotFoundError:
        return {"error": f"Fichier {config_name}.json non trouvé", "status": 404}
    except json.JSONDecodeError as e:
        return {"error": f"JSON invalide: {str(e)}", "status": 400}


@router.get("/drugs")
async def get_drugs() -> dict[str, Any]:
    """Récupère la liste des drogues anesthésiques disponibles.

    Returns:
        Dict avec liste des drogues (nom, code_central, concentration, unit, min/max/optimal).
    """
    # Charger les drogues depuis protocoles_suivi.json (qui contient les codes ERP)
    try:
        protocols_file = Path(__file__).parent.parent.parent.parent / "protocoles_suivi.json"
        with open(protocols_file) as f:
            protocols = json.load(f)

        # Extraire les drogues uniques avec leurs infos
        drugs_dict = {}
        for protocol in protocols:
            for drug in protocol.get("drugs", []):
                key = drug.get("code_central") or drug.get("name")
                if key not in drugs_dict:
                    drugs_dict[key] = {
                        "name": drug.get("name"),
                        "commercial": drug.get("commercial"),
                        "code_central": drug.get("code_central"),
                        "concentration": drug.get("concentration"),
                        "unit": drug.get("unit"),
                    }

        return {"success": True, "drugs": list(drugs_dict.values())}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/injectable-products")
async def get_injectable_products() -> dict[str, Any]:
    """Récupère les produits injectables disponibles depuis l'ERP.

    Returns:
        Dict avec liste des produits (gtin, nom, concentration, unit, route).
    """
    return await DashboardService.get_injectable_products()


@router.post("/config/{config_name}")
async def update_config(config_name: str, body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Met à jour un fichier de configuration JSON.

    Args:
        config_name: Nom du fichier (acts, protocols, protocoles_suivi, presets)
        body: Dict avec clé 'data' contenant le nouveau JSON

    Returns:
        Status de mise à jour.
    """
    allowed_files = {"acts", "protocols", "protocoles_suivi", "presets"}
    if config_name not in allowed_files:
        return {"success": False, "error": "Configuration invalide"}

    if "data" not in body:
        return {"success": False, "error": "Clé 'data' manquante"}

    config_file = Path(__file__).parent.parent.parent.parent / f"{config_name}.json"
    try:
        # Valider que c'est du JSON valide
        data = body["data"]
        if isinstance(data, str):
            data = json.loads(data)

        # Écrire le fichier
        with open(config_file, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return {
            "success": True,
            "config": config_name,
            "message": f"{config_name}.json mis à jour avec succès",
        }
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"JSON invalide: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Erreur lors de la sauvegarde: {str(e)}"}
