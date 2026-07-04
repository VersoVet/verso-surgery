"""Service de proxy pour erp-connector."""

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class DashboardService:
    """Proxy service pour accès erp-connector depuis le dashboard."""

    ERP_BASE_URL = "http://10.0.0.44:8101"
    TIMEOUT = 30.0

    @classmethod
    async def get_rdv_today(cls) -> list[dict[str, Any]]:
        """Récupère les rendez-vous du jour.

        Returns:
            Liste des RDV d'aujourd'hui.
        """
        try:
            async with httpx.AsyncClient(timeout=cls.TIMEOUT) as client:
                response = await client.get(
                    f"{cls.ERP_BASE_URL}/appointments",
                    params={"from": "today", "to": "today"},
                )
                response.raise_for_status()
                data: Any = response.json()
                if isinstance(data, dict):
                    rdv_list = data.get("appointments", [])
                    return rdv_list if isinstance(rdv_list, list) else []
                return []
        except Exception as e:
            logger.warning(f"Failed to get RDV today: {e}")
            return []

    @classmethod
    async def search_patient(cls, q: str) -> list[dict[str, Any]]:
        """Recherche un animal ou propriétaire.

        Args:
            q: Terme de recherche

        Returns:
            Liste des résultats de recherche.
        """
        try:
            async with httpx.AsyncClient(timeout=cls.TIMEOUT) as client:
                response = await client.get(
                    f"{cls.ERP_BASE_URL}/search",
                    params={"q": q},
                )
                response.raise_for_status()
                data: Any = response.json()
                if isinstance(data, dict):
                    results = data.get("results", [])
                    return results if isinstance(results, list) else []
                return []
        except Exception as e:
            logger.warning(f"Failed to search patient: {e}")
            return []

    @classmethod
    async def get_animal(cls, animal_id: int) -> dict[str, Any] | None:
        """Récupère les détails d'un animal.

        Args:
            animal_id: ID VetoPartner de l'animal

        Returns:
            Dict avec infos animal ou None.
        """
        try:
            async with httpx.AsyncClient(timeout=cls.TIMEOUT) as client:
                response = await client.get(
                    f"{cls.ERP_BASE_URL}/animals/{animal_id}",
                )
                response.raise_for_status()
                data: Any = response.json()
                return data if isinstance(data, dict) else None
        except Exception as e:
            logger.warning(f"Failed to get animal {animal_id}: {e}")
            return None

    @classmethod
    async def create_consultation(
        cls,
        animal_id: int,
        text: str,
        consult_type: str = "surgery",
    ) -> dict[str, Any]:
        """Crée une consultation VetoPartner.

        Args:
            animal_id: ID de l'animal
            text: Texte de la consultation
            consult_type: Type de consultation

        Returns:
            Dict avec status et ID consultation créée.
        """
        try:
            async with httpx.AsyncClient(timeout=cls.TIMEOUT) as client:
                response = await client.post(
                    f"{cls.ERP_BASE_URL}/animals/{animal_id}/consultations",
                    json={
                        "text": text,
                        "type": consult_type,
                    },
                )
                response.raise_for_status()
                result: Any = response.json()

                return {
                    "success": True,
                    "consultation_id": result.get("id")
                    or result.get("consultation_id"),
                    "animal_id": animal_id,
                }
        except Exception as e:
            logger.error(f"Failed to create consultation: {e}")
            return {
                "success": False,
                "error": f"Erreur lors de création consultation: {str(e)}",
                "consultation_id": None,
            }
