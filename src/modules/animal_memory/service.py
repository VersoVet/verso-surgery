"""Service de mémoire des traitements par animal."""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any

from src.modules.animal_memory.store import (
    db_get_last_session,
    db_insert_or_replace_treatment,
)

logger = logging.getLogger(__name__)


async def get_last_session(animal_id: int, act_id: str) -> dict[str, Any] | None:
    """Récupère la dernière séance d'un acte (async wrapper).

    Args:
        animal_id: ID VetoPartner de l'animal.
        act_id: ID de l'acte.

    Returns:
        Dict avec date, num_seance (int), act_name, fields ou None.
    """
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _get_last_session_sync, animal_id, act_id)
    return result


def _get_last_session_sync(animal_id: int, act_id: str) -> dict[str, Any] | None:
    """Récupère la dernière séance (sync).

    Args:
        animal_id: ID VetoPartner de l'animal.
        act_id: ID de l'acte.

    Returns:
        Dict avec date, num_seance (int), act_name, fields ou None.
    """
    row = db_get_last_session(animal_id, act_id)
    if not row:
        return None

    fields = row.get("fields", {})
    num_seance_str = fields.get("N° de séance", "0")
    try:
        num_seance = int(num_seance_str)
    except (ValueError, TypeError):
        num_seance = 0

    return {
        "date": row.get("date"),
        "num_seance": num_seance,
        "act_name": row.get("act_name"),
        "fields": fields,
    }


async def update_animal_memory(
    animal_id: int,
    animal_nom: str,
    date: str,
    appointment_id: str,
    actes: list[dict[str, Any]],
) -> None:
    """Met à jour la mémoire animale pour les actes avec 'N° de séance' (async).

    Args:
        animal_id: ID VetoPartner de l'animal.
        animal_nom: Nom de l'animal.
        date: Date YYYY-MM-DD.
        appointment_id: ID du rendez-vous.
        actes: Liste des actes validés (payload de validateActes).

    Returns:
        None
    """
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        _update_animal_memory_sync,
        animal_id,
        animal_nom,
        date,
        appointment_id,
        actes,
    )


def _update_animal_memory_sync(
    animal_id: int,
    animal_nom: str,
    date: str,
    appointment_id: str,
    actes: list[dict[str, Any]],
) -> None:
    """Met à jour la mémoire animale (sync).

    Seuls les actes avec 'N° de séance' dans fields sont mémorisés.

    Args:
        animal_id: ID VetoPartner de l'animal.
        animal_nom: Nom de l'animal.
        date: Date YYYY-MM-DD.
        appointment_id: ID du rendez-vous.
        actes: Liste des actes validés.

    Returns:
        None
    """
    now = datetime.utcnow().isoformat()

    for acte in actes:
        act_id = acte.get("act_id")
        act_name = acte.get("act_name", "?")
        fields = acte.get("fields", {})

        # Seuls les actes avec 'N° de séance' sont mémorisés
        if "N° de séance" not in fields:
            continue

        fields_json = json.dumps(fields)

        try:
            db_insert_or_replace_treatment(
                animal_id=animal_id,
                animal_nom=animal_nom,
                appointment_id=appointment_id,
                date=date,
                act_id=act_id,
                act_name=act_name,
                fields_json=fields_json,
                created_at=now,
            )
        except Exception as e:
            logger.error(f"Failed to update animal memory for {animal_id}/{act_id}: {e}")
