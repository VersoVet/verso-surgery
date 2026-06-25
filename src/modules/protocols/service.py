"""Service de gestion des protocoles anesthésiques."""

import json
from pathlib import Path
from typing import Any

from src.models import Protocol


class ProtocolService:
    """Service pour accéder aux protocoles anesthésiques."""

    _protocols_cache: list[Protocol] | None = None

    @classmethod
    def load_protocols(cls) -> list[Protocol]:
        """Charge les protocoles depuis protocols.json.

        Returns:
            Liste des protocoles anesthésiques disponibles.
        """
        if cls._protocols_cache is not None:
            return cls._protocols_cache

        protocols_path = Path(__file__).parent.parent.parent.parent / "protocols.json"
        with open(protocols_path) as f:
            data = json.load(f)

        cls._protocols_cache = [Protocol(**p) for p in data]
        return cls._protocols_cache

    @classmethod
    def get_protocol(cls, protocol_id: str) -> Protocol | None:
        """Récupère un protocole par ID.

        Args:
            protocol_id: ID du protocole (ex: "mk_standard")

        Returns:
            Le protocole ou None si non trouvé.
        """
        protocols = cls.load_protocols()
        return next((p for p in protocols if p.id == protocol_id), None)

    @classmethod
    def get_protocols_for_species(cls, species: str) -> list[Protocol]:
        """Liste les protocoles disponibles pour une espèce.

        Args:
            species: Espèce (chien ou chat)

        Returns:
            Liste des protocoles disponibles pour cette espèce.
        """
        protocols = cls.load_protocols()
        return [p for p in protocols if species in p.species]

    @classmethod
    def calculate_dose(
        cls, protocol_id: str, weight_kg: float
    ) -> dict[str, Any] | None:
        """Calcule les doses pour un protocole et poids.

        Args:
            protocol_id: ID du protocole
            weight_kg: Poids de l'animal en kg

        Returns:
            Dict avec doses calculées ou None si protocole invalide.
        """
        protocol = cls.get_protocol(protocol_id)
        if not protocol:
            return None

        doses = []
        for drug in protocol.drugs:
            dose_mg = drug.dose * weight_kg
            volume_ml = dose_mg / drug.concentration

            doses.append(
                {
                    "drug_name": drug.name,
                    "commercial_name": drug.commercial,
                    "dose_mg": round(dose_mg, 2),
                    "volume_ml": round(volume_ml, 2),
                    "route": drug.route,
                    "phase": drug.phase,
                    "concentration": drug.concentration,
                    "unit": drug.unit,
                }
            )

        return {
            "protocol_id": protocol_id,
            "protocol_name": protocol.name,
            "weight_kg": weight_kg,
            "doses": doses,
        }
