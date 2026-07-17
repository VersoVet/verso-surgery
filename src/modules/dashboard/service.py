"""Service de proxy pour erp-connector."""

import logging
from typing import Any

import httpx
from erp_ui_sdk import (
    AppointmentService,
    ErpClient,
    SiteService,
    VetService,
)

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
    async def get_sites(cls) -> dict[str, Any]:
        """Récupère tous les sites.

        Returns:
            Dict avec liste des sites.
        """
        try:
            client = ErpClient(base_url=cls.ERP_BASE_URL, timeout=cls.TIMEOUT)
            sites = await SiteService.list(client)
            return {
                "sites": [site.model_dump() for site in sites],
            }
        except Exception as e:
            logger.warning(f"Failed to get sites: {e}")
            return {"sites": []}

    @classmethod
    async def get_vets(cls) -> dict[str, Any]:
        """Récupère tous les vétérinaires.

        Returns:
            Dict avec liste des vétérinaires.
        """
        try:
            client = ErpClient(base_url=cls.ERP_BASE_URL, timeout=cls.TIMEOUT)
            vets = await VetService.list(client)
            return {
                "vets": [vet.model_dump() for vet in vets],
            }
        except Exception as e:
            logger.warning(f"Failed to get vets: {e}")
            return {"vets": []}

    @classmethod
    async def get_appointments(
        cls,
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
        try:
            client = ErpClient(base_url=cls.ERP_BASE_URL, timeout=cls.TIMEOUT)
            appointments = await AppointmentService.get_range(client, date_from, date_to, vet_id, site_id)
            return {
                "appointments": [apt.model_dump() for apt in appointments],
            }
        except Exception as e:
            logger.warning(f"Failed to get appointments: {e}")
            return {"appointments": []}

    @classmethod
    async def create_consultation(
        cls,
        animal_id: int,
        synthese: str,
        motif: str = "Chirurgie",
        veto_id: int | None = None,
        site_id: int | None = None,
    ) -> dict[str, Any]:
        """Crée une consultation VetoPartner.

        Args:
            animal_id: ID de l'animal
            synthese: Synthèse de la consultation
            motif: Motif de la consultation
            veto_id: ID du vétérinaire optionnel
            site_id: ID du site optionnel

        Returns:
            Dict avec status et ID consultation créée.
        """
        try:
            async with httpx.AsyncClient(timeout=cls.TIMEOUT) as client:
                body: dict[str, Any] = {
                    "animal_id": animal_id,
                    "synthese": synthese,
                    "motif": motif,
                }
                if veto_id is not None:
                    body["veto_id"] = veto_id
                if site_id is not None:
                    body["site_id"] = site_id

                logger.debug(f"POST /consultations: animal_id={animal_id}, synthese_len={len(synthese)}, motif={motif}")
                response = await client.post(
                    f"{cls.ERP_BASE_URL}/consultations",
                    json=body,
                )
                response.raise_for_status()
                result: Any = response.json()

                return {
                    "success": True,
                    "consultation_id": result.get("id"),
                    "animal_id": animal_id,
                }
        except httpx.HTTPStatusError as e:
            error_detail = f"HTTP {e.response.status_code}: {e.response.text[:200]}"
            logger.error(f"Failed to create consultation: {error_detail}")
            return {
                "success": False,
                "error": f"Erreur lors de création consultation: {error_detail}",
                "consultation_id": None,
            }
        except Exception as e:
            logger.error(f"Failed to create consultation: {e}")
            return {
                "success": False,
                "error": f"Erreur lors de création consultation: {str(e)}",
                "consultation_id": None,
            }

    @classmethod
    async def search_erp_products(cls, search: str = "") -> dict[str, Any]:
        """Recherche des produits dans l'ERP.

        Args:
            search: Terme de recherche (designation du produit).

        Returns:
            Dict avec liste des produits ERP (id, designation, codecentrale).
        """
        try:
            async with httpx.AsyncClient(timeout=cls.TIMEOUT) as client:
                params: dict[str, Any] = {"limit": 30}
                if search:
                    params["search"] = search
                response = await client.get(
                    f"{cls.ERP_BASE_URL}/produits",
                    params=params,
                )
                response.raise_for_status()
                data: Any = response.json()

                products = []
                for prod in data.get("products", []):
                    products.append(
                        {
                            "id": prod.get("id"),
                            "designation": prod.get("designation", ""),
                            "code_central": prod.get("codecentrale", ""),
                        }
                    )

                return {"success": True, "products": products}
        except Exception as e:
            logger.warning(f"Failed to search ERP products: {e}")
            return {"success": False, "error": str(e), "products": []}

    @classmethod
    async def create_ordonnance(
        cls,
        animal_id: int,
        lignes: list[dict[str, Any]],
        veto_id: int | None = None,
        site_id: int = 2,
    ) -> dict[str, Any]:
        """Crée une ordonnance VetoPartner.

        Args:
            animal_id: ID de l'animal
            lignes: Lignes d'ordonnance [{designation, quantite, notes}]
            veto_id: ID du vétérinaire
            site_id: ID du site (défaut: 2)

        Returns:
            Dict avec success et ordonnance_id.
        """
        try:
            async with httpx.AsyncClient(timeout=cls.TIMEOUT) as client:
                body: dict[str, Any] = {
                    "lignes": lignes,
                    "type_ordo": 1,
                    "id_site": site_id,
                }
                if veto_id is not None:
                    body["veto_id"] = veto_id
                response = await client.post(
                    f"{cls.ERP_BASE_URL}/animals/{animal_id}/ordonnances",
                    json=body,
                )
                response.raise_for_status()
                result: Any = response.json()

                return {
                    "success": True,
                    "ordonnance_id": result.get("id"),
                    "animal_id": animal_id,
                }
        except Exception as e:
            logger.error(f"Failed to create ordonnance: {e}")
            return {
                "success": False,
                "error": f"Erreur lors de création ordonnance: {str(e)}",
                "ordonnance_id": None,
            }
