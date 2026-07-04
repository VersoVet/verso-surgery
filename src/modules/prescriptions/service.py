"""Service d'intégration avec erp-connector pour les ordonnances."""

import logging
from typing import Any, cast

import httpx

from src.models import Surgery

logger = logging.getLogger(__name__)


class PrescriptionService:
    """Service pour créer des ordonnances via erp-connector."""

    ERP_BASE_URL = "http://10.0.0.44:8101"
    TIMEOUT = 30.0

    @classmethod
    async def search_product_by_code_central(
        cls,
        code_central: str,
    ) -> dict[str, Any] | None:
        """Recherche un produit par code central.

        Args:
            code_central: Code central VetoPartner (ex: "10341")

        Returns:
            Dict avec info du produit si trouvé, None sinon.
        """
        try:
            async with httpx.AsyncClient(timeout=cls.TIMEOUT) as client:
                response = await client.get(
                    f"{cls.ERP_BASE_URL}/produits",
                    params={"code_central": code_central},
                )
                response.raise_for_status()
                data: Any = response.json()

                # Récupérer le premier produit si disponible
                if isinstance(data, dict):
                    products = data.get("products", [])
                    if products and len(products) > 0:
                        return cast(dict[str, Any], products[0])
                return None
        except Exception as e:
            logger.warning(f"Product search failed for code {code_central}: {e}")
            return None

    @classmethod
    async def search_product_by_designation(
        cls,
        designation: str,
    ) -> dict[str, Any] | None:
        """Recherche un produit par nom/designation.

        Args:
            designation: Nom du médicament à chercher

        Returns:
            Dict avec info du produit si trouvé, None sinon.
        """
        try:
            async with httpx.AsyncClient(timeout=cls.TIMEOUT) as client:
                response = await client.get(
                    f"{cls.ERP_BASE_URL}/produits",
                    params={"search": designation, "limit": 5},
                )
                response.raise_for_status()
                data: Any = response.json()

                # Retourner le premier produit si disponible
                if isinstance(data, dict):
                    products = data.get("products", [])
                    if products and len(products) > 0:
                        return cast(dict[str, Any], products[0])
                return None
        except Exception as e:
            logger.warning(f"Product search failed for {designation}: {e}")
            return None

    @classmethod
    async def create_ordonnance(
        cls,
        animal_id: str,
        surgery: Surgery,
        veto_id: int | None = None,
        veto_nom: str | None = None,
    ) -> dict[str, Any]:
        """Crée une ordonnance anesthésique via erp-connector.

        Utilise la nouvelle API erp-connector avec code_central et auto-enrichissement.
        Les lignes sans code_central sont créées comme "hors_stock" avec designation.

        Args:
            animal_id: ID de l'animal (numérique dans VetoPartner)
            surgery: Chirurgie avec doses calculées
            veto_id: ID du vétérinaire (optionnel)
            veto_nom: Nom du vétérinaire (optionnel)

        Returns:
            Dict avec status et détails de l'ordonnance créée.
        """
        # Construire les lignes d'ordonnance
        lignes = []
        for dose in surgery.doses:
            # Chercher le produit (optionnel, pour enrichissement)
            product = await cls.search_product_by_designation(dose.commercial_name)

            # Construire la ligne
            # Si on trouve un produit avec code_central, l'utiliser
            # Sinon, utiliser designation avec type hors_stock
            ligne: dict[str, Any] = {
                "quantite": 1,
                "notes": f"{dose.dose_mg:.2f}mg ({dose.volume_ml:.2f}mL) - {dose.route} - {dose.phase}",
            }

            if product and product.get("codecentrale"):
                # Utiliser le code central trouvé
                ligne["code_central"] = product["codecentrale"]
            else:
                # Créer comme hors_stock avec designation
                ligne["designation"] = dose.commercial_name
                ligne["type_ligne"] = "hors_stock"

            lignes.append(ligne)

        # Créer l'ordonnance via erp-connector
        try:
            async with httpx.AsyncClient(timeout=cls.TIMEOUT) as client:
                # Valider animal_id numérique
                try:
                    animal_id_int = int(animal_id)
                except ValueError:
                    return {
                        "success": False,
                        "error": f"animal_id doit être numérique: {animal_id}",
                        "ordonnance_id": None,
                    }

                ordonnance_data = {
                    "veto_id": veto_id,
                    "veto_nom": veto_nom,
                    "type_ordo": 1,  # Prescription uniquement
                    "id_site": 2,  # Site par défaut
                    "lignes": lignes,
                }

                response = await client.post(
                    f"{cls.ERP_BASE_URL}/animals/{animal_id_int}/ordonnances",
                    json=ordonnance_data,
                )
                response.raise_for_status()
                result: Any = response.json()

                return {
                    "success": True,
                    "ordonnance_id": result.get("id") or result.get("ordonnance_id"),
                    "surgery_id": surgery.id,
                    "animal_id": animal_id,
                    "lignes_count": len(lignes),
                    "message": f"Ordonnance créée ({len(lignes)} lignes)",
                }
        except Exception as e:
            logger.error(f"Failed to create ordonnance: {e}")
            return {
                "success": False,
                "error": f"Erreur lors de la création de l'ordonnance: {str(e)}",
                "ordonnance_id": None,
            }
