"""Service de gestion du suivi de prise en charge."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from src.models import (
    ActesRequest,
    AnesthesieRequest,
    ArriveRequest,
    ProtocolSuivi,
    SortieRequest,
    StageStatus,
    SuiviStageData,
    SuiviTracking,
)
from src.modules.dashboard.service import DashboardService
from src.modules.suivi.formatter import format_consultation
from src.modules.suivi.store import load_tracking, save_tracking

logger = logging.getLogger(__name__)

_protocols_cache: list[ProtocolSuivi] | None = None


def load_suivi_protocols() -> list[ProtocolSuivi]:
    """Charge les protocoles anesthésiques pour suivi.

    Returns:
        Liste des protocoles suivi.
    """
    global _protocols_cache
    if _protocols_cache is not None:
        return _protocols_cache

    try:
        protocols_file = Path(__file__).parent.parent.parent.parent / "protocoles_suivi.json"
        with open(protocols_file) as f:
            data = json.load(f)
            _protocols_cache = [ProtocolSuivi(**p) for p in data]
            logger.info(f"✓ Loaded {len(_protocols_cache)} suivi protocols")
            return _protocols_cache
    except Exception as e:
        logger.error(f"Failed to load suivi protocols: {e}")
        return []


def calculate_doses(protocol: ProtocolSuivi, poids_kg: float) -> list[dict[str, Any]]:
    """Calcule les doses pour un protocole et un poids donnés.

    Args:
        protocol: Protocole anesthésique.
        poids_kg: Poids de l'animal en kg.

    Returns:
        Liste des doses calculées.
    """
    doses = []
    for drug in protocol.drugs:
        # Sauter les drugs sans dose (comme Isoflurane inhalé)
        if drug.dose == 0.0 and drug.dose_unit == "mg/kg":
            doses.append(
                {
                    "name": drug.name,
                    "commercial": drug.commercial,
                    "concentration": drug.concentration,
                    "unit": drug.unit,
                    "dose_mg": 0.0,
                    "volume_ml": 0.0,
                    "dose_min": drug.dose_min,
                    "dose_max": drug.dose_max,
                    "volume_min_ml": 0.0,
                    "volume_max_ml": 0.0,
                    "route": drug.route,
                    "phase": drug.phase,
                    "optional": drug.optional,
                    "code_central": drug.code_central,
                    "selected": not drug.optional,
                }
            )
            continue

        # Calculer la dose totale
        dose_mg = drug.dose * poids_kg
        volume_ml = dose_mg / drug.concentration
        dose_min_mg = drug.dose_min * poids_kg if drug.dose_min > 0 else dose_mg
        dose_max_mg = drug.dose_max * poids_kg if drug.dose_max > 0 else dose_mg
        volume_min_ml = dose_min_mg / drug.concentration
        volume_max_ml = dose_max_mg / drug.concentration

        doses.append(
            {
                "name": drug.name,
                "commercial": drug.commercial,
                "concentration": drug.concentration,
                "unit": drug.unit,
                "dose_mg": round(dose_mg, 2),
                "volume_ml": round(volume_ml, 2),
                "dose_min": round(dose_min_mg, 2),
                "dose_max": round(dose_max_mg, 2),
                "volume_min_ml": round(volume_min_ml, 2),
                "volume_max_ml": round(volume_max_ml, 2),
                "route": drug.route,
                "phase": drug.phase,
                "optional": drug.optional,
                "code_central": drug.code_central,
                "selected": not drug.optional,
            }
        )

    return doses


async def process_arrivee(req: ArriveRequest) -> SuiviTracking:
    """Traite l'arrivée du patient — étape 1.

    Args:
        req: Données d'arrivée.

    Returns:
        Tracking créé/mis à jour.
    """
    now = datetime.utcnow().isoformat()

    # Charger le tracking s'il existe
    tracking = load_tracking(req.appointment_id)

    if tracking is None:
        # Créer un nouveau tracking
        tracking = SuiviTracking(
            appointment_id=req.appointment_id,
            animal_id=req.animal_id,
            animal_nom=req.animal_nom,
            espece=req.espece,
            poids_kg=req.poids_kg,
            client_nom=req.client_nom,
            client_prenom=req.client_prenom,
            vet_id=req.vet_id,
            site_id=req.site_id,
            date_rdv=req.date_rdv,
            created_at=now,
            updated_at=now,
            current_stage="arrivee",
            stages={
                "arrivee": SuiviStageData(status=StageStatus.DONE, timestamp=now, data={}),
                "anesthesie": SuiviStageData(status=StageStatus.PENDING, timestamp=None, data={}),
                "actes": SuiviStageData(status=StageStatus.PENDING, timestamp=None, data={}),
                "sortie": SuiviStageData(status=StageStatus.PENDING, timestamp=None, data={}),
            },
        )
    else:
        # Mettre à jour le tracking existant
        tracking.poids_kg = req.poids_kg
        tracking.updated_at = now
        tracking.stages["arrivee"] = SuiviStageData(
            status=StageStatus.DONE, timestamp=now, data={}
        )

    save_tracking(tracking)
    logger.info(f"Arrivée processed for appointment {req.appointment_id}")
    return tracking


async def process_anesthesie(req: AnesthesieRequest) -> dict[str, Any]:
    """Traite l'anesthésie — étape 2 avec création d'ordonnance.

    Args:
        req: Données d'anesthésie.

    Returns:
        Dict avec success, tracking, ordonnance_id.
    """
    now = datetime.utcnow().isoformat()

    # Charger le tracking
    tracking = load_tracking(req.appointment_id)
    if not tracking:
        return {"success": False, "error": "Tracking not found"}

    # Builder les lignes ordonnance
    lignes = _build_ordonnance_lignes(req.doses)

    # Créer l'ordonnance via DashboardService
    try:
        ordo_result = await DashboardService.create_ordonnance(
            animal_id=tracking.animal_id,
            lignes=lignes,
            veto_id=req.veto_id,
            site_id=req.site_id,
        )
        if not ordo_result.get("success"):
            return {"success": False, "error": f"Ordonnance creation failed: {ordo_result}"}
    except Exception as e:
        logger.error(f"Ordonnance creation error: {e}")
        return {"success": False, "error": str(e)}

    # Sauvegarder dans le tracking
    tracking.current_stage = "anesthesie"
    tracking.updated_at = now
    tracking.stages["anesthesie"] = SuiviStageData(
        status=StageStatus.DONE,
        timestamp=now,
        data={
            "protocol_id": req.protocol_id,
            "poids_kg": req.poids_kg,
            "doses": req.doses,
            "ordonnance_id": ordo_result.get("ordonnance_id"),
        },
    )

    save_tracking(tracking)
    logger.info(f"Anesthésie processed for appointment {req.appointment_id}")
    return {
        "success": True,
        "tracking": tracking.model_dump(),
        "ordonnance_id": ordo_result.get("ordonnance_id"),
    }


async def process_actes(req: ActesRequest) -> SuiviTracking:
    """Traite les actes/soins — étape 3.

    Args:
        req: Données des actes.

    Returns:
        Tracking mis à jour.
    """
    now = datetime.utcnow().isoformat()

    tracking = load_tracking(req.appointment_id)
    if not tracking:
        raise ValueError("Tracking not found")

    tracking.current_stage = "actes"
    tracking.updated_at = now
    tracking.stages["actes"] = SuiviStageData(
        status=StageStatus.DONE,
        timestamp=now,
        data={"actes": req.actes},
    )

    save_tracking(tracking)
    logger.info(f"Actes processed for appointment {req.appointment_id}")
    return tracking


async def process_sortie(req: SortieRequest) -> dict[str, Any]:
    """Traite la sortie — étape 4 avec création de consultation.

    Args:
        req: Données de sortie.

    Returns:
        Dict avec success, tracking, consultation_id.
    """
    now = datetime.utcnow().isoformat()

    tracking = load_tracking(req.appointment_id)
    if not tracking:
        return {"success": False, "error": "Tracking not found"}

    # Créer la consultation via DashboardService
    try:
        consult_result = await DashboardService.create_consultation(
            animal_id=tracking.animal_id,
            synthese=req.synthese,
            motif="Chirurgie / Suivi",
            veto_id=req.veto_id,
            site_id=req.site_id,
        )
        if not consult_result.get("success"):
            return {
                "success": False,
                "error": f"Consultation creation failed: {consult_result}",
            }
    except Exception as e:
        logger.error(f"Consultation creation error: {e}")
        return {"success": False, "error": str(e)}

    # Marquer comme terminé
    tracking.current_stage = "termine"
    tracking.updated_at = now
    tracking.stages["sortie"] = SuiviStageData(
        status=StageStatus.DONE,
        timestamp=now,
        data={
            "synthese": req.synthese,
            "consultation_id": consult_result.get("consultation_id"),
        },
    )

    save_tracking(tracking)
    logger.info(f"Sortie processed for appointment {req.appointment_id}")
    return {
        "success": True,
        "tracking": tracking.model_dump(),
        "consultation_id": consult_result.get("consultation_id"),
    }


def get_preview(appointment_id: str) -> str:
    """Génère un aperçu du compte-rendu avant validation.

    Args:
        appointment_id: ID du rendez-vous.

    Returns:
        Texte formaté du CR.
    """
    tracking = load_tracking(appointment_id)
    if not tracking:
        return ""

    return format_consultation(tracking)


def _build_ordonnance_lignes(doses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Construit les lignes d'ordonnance depuis les doses sélectionnées.

    Args:
        doses: Liste des doses avec selections.

    Returns:
        Liste des lignes ordonnance pour VetoPartner.
    """
    lignes = []
    for dose in doses:
        if not dose.get("selected", True):
            continue

        volume_ml = dose.get("volume_ml", 0)
        route = dose.get("route", "?")
        phase = dose.get("phase", "?")
        notes = f"{volume_ml:.2f} mL — {route} — {phase}"

        ligne: dict[str, Any] = {
            "designation": dose.get("commercial", dose.get("name", "?")),
            "quantite": 1,
            "notes": notes,
        }

        # Si code_central présent → type produit, sinon hors_stock
        if dose.get("code_central"):
            ligne["type_ligne"] = "produit"
            ligne["code_central"] = dose["code_central"]
        else:
            ligne["type_ligne"] = "hors_stock"

        lignes.append(ligne)

    return lignes
