"""Persistence des états de suivi sur disque."""

import json
import logging
from pathlib import Path

from src.models import SuiviTracking

logger = logging.getLogger(__name__)

DATA_DIR = Path("/opt/onyx/data/verso-surgery/suivi")


def ensure_data_dir() -> None:
    """Crée le répertoire de données s'il n'existe pas.

    Returns:
        None
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"✓ Suivi data directory ensured: {DATA_DIR}")


def _get_file_path(appointment_id: str) -> Path:
    """Retourne le chemin du fichier de tracking.

    Args:
        appointment_id: ID du rendez-vous.

    Returns:
        Path du fichier JSON.
    """
    return DATA_DIR / f"{appointment_id}.json"


def load_tracking(appointment_id: str) -> SuiviTracking | None:
    """Charge l'état de suivi d'un rendez-vous.

    Args:
        appointment_id: ID du rendez-vous.

    Returns:
        SuiviTracking ou None si absent.
    """
    file_path = _get_file_path(appointment_id)
    if not file_path.exists():
        return None

    try:
        content = file_path.read_text()
        data = json.loads(content)
        return SuiviTracking(**data)
    except Exception as e:
        logger.error(f"Failed to load tracking {appointment_id}: {e}")
        return None


def save_tracking(tracking: SuiviTracking) -> None:
    """Sauvegarde l'état de suivi d'un rendez-vous.

    Args:
        tracking: État de suivi à sauvegarder.

    Returns:
        None
    """
    file_path = _get_file_path(tracking.appointment_id)
    try:
        content = json.dumps(tracking.model_dump(), indent=2, ensure_ascii=False)
        file_path.write_text(content)
    except Exception as e:
        logger.error(f"Failed to save tracking {tracking.appointment_id}: {e}")


def list_today_trackings(date: str) -> list[SuiviTracking]:
    """Liste tous les trackings du jour.

    Args:
        date: Date au format YYYY-MM-DD.

    Returns:
        Liste des SuiviTracking.
    """
    trackings = []
    try:
        for file_path in DATA_DIR.glob("*.json"):
            tracking = load_tracking(file_path.stem)
            if tracking and tracking.date_rdv == date:
                trackings.append(tracking)
    except Exception as e:
        logger.error(f"Failed to list today's trackings for {date}: {e}")

    return trackings


def delete_tracking(appointment_id: str) -> bool:
    """Supprime l'état de suivi d'un rendez-vous.

    Args:
        appointment_id: ID du rendez-vous.

    Returns:
        True si suppression réussie, False sinon.
    """
    file_path = _get_file_path(appointment_id)
    try:
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to delete tracking {appointment_id}: {e}")
        return False
