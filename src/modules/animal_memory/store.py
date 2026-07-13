"""Stockage SQLite pour mémoire des traitements par animal."""

import json
import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path("/opt/onyx/data/verso-surgery/verso_surgery.db")


def ensure_db() -> None:
    """Crée la DB et les tables si inexistantes.

    Returns:
        None
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Table principal pour les traitements
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS animal_treatments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            animal_id INTEGER NOT NULL,
            animal_nom TEXT NOT NULL,
            appointment_id TEXT NOT NULL,
            date TEXT NOT NULL,
            act_id TEXT NOT NULL,
            act_name TEXT NOT NULL,
            fields_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(appointment_id, act_id)
        )
    """
    )

    # Index pour recherche rapide par animal + acte
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_animal_act
        ON animal_treatments(animal_id, act_id)
    """
    )

    conn.commit()
    conn.close()


def get_connection() -> sqlite3.Connection:
    """Retourne une connexion SQLite avec row_factory.

    Returns:
        Connexion SQLite.
    """
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def db_insert_or_replace_treatment(
    animal_id: int,
    animal_nom: str,
    appointment_id: str,
    date: str,
    act_id: str,
    act_name: str,
    fields_json: str,
    created_at: str,
) -> None:
    """Insère ou remplace un traitement (idempotent par appointment_id + act_id).

    Args:
        animal_id: ID VetoPartner de l'animal.
        animal_nom: Nom de l'animal.
        appointment_id: ID du rendez-vous.
        date: Date YYYY-MM-DD.
        act_id: ID de l'acte.
        act_name: Nom de l'acte.
        fields_json: Champs serialisés en JSON.
        created_at: Timestamp ISO UTC.

    Returns:
        None
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR REPLACE INTO animal_treatments
        (animal_id, animal_nom, appointment_id, date, act_id, act_name, fields_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (animal_id, animal_nom, appointment_id, date, act_id, act_name, fields_json, created_at),
    )

    conn.commit()
    conn.close()


def db_get_last_session(animal_id: int, act_id: str) -> dict[str, Any] | None:
    """Récupère la dernière séance d'un acte pour un animal.

    Args:
        animal_id: ID VetoPartner de l'animal.
        act_id: ID de l'acte.

    Returns:
        Dict avec date, act_name, fields ou None si absent.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT date, act_name, fields_json
        FROM animal_treatments
        WHERE animal_id = ? AND act_id = ?
        ORDER BY date DESC, id DESC
        LIMIT 1
    """,
        (animal_id, act_id),
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    try:
        fields = json.loads(row["fields_json"])
    except (json.JSONDecodeError, ValueError):
        fields = {}

    return {
        "date": row["date"],
        "act_name": row["act_name"],
        "fields": fields,
    }
