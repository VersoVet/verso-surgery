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
    async def check_medicine_in_stock(
        cls,
        medicine_name: str,
    ) -> dict[str, Any] | None:
        """Vérifie qu'un médicament est disponible en stock.

        Args:
            medicine_name: Nom du médicament à chercher

        Returns:
            Dict avec info du produit si trouvé, None sinon.
        """
        try:
            async with httpx.AsyncClient(timeout=cls.TIMEOUT) as client:
                response = await client.get(
                    f"{cls.ERP_BASE_URL}/produits",
                    params={"search": medicine_name, "limit": 10},
                )
                response.raise_for_status()
                data: Any = response.json()

                # data est une liste de produits
                if isinstance(data, list) and len(data) > 0:
                    # Retourner le premier match exact ou fuzzy
                    for product in data:
                        product_dict: dict[str, Any] = cast(dict[str, Any], product)
                        if product_dict.get("designation", "").lower() == medicine_name.lower():
                            return product_dict
                    # Si pas de match exact, retourner le premier résultat
                    return cast(dict[str, Any], data[0])
                return None
        except Exception as e:
            logger.warning(f"Stock check failed for {medicine_name}: {e}")
            return None

    @classmethod
    async def validate_anesthetic_prescription(
        cls,
        surgery: Surgery,
    ) -> tuple[bool, str]:
        """Valide qu'une ordonnance anesthésique utilise des médicaments en stock.

        Args:
            surgery: Chirurgie avec doses anesthésiques calculées

        Returns:
            Tuple (valid, message)
        """
        missing = []

        for dose in surgery.doses:
            # Chercher le médicament dans le stock
            product = await cls.check_medicine_in_stock(dose.commercial_name)
            if not product:
                missing.append(dose.commercial_name)

        if missing:
            msg = f"Médicaments non disponibles en stock: {', '.join(missing)}"
            return False, msg

        return True, "Tous les médicaments sont disponibles en stock"

    @classmethod
    async def create_ordonnance(
        cls,
        animal_id: str,
        surgery: Surgery,
        veto_id: int | None = None,
        veto_nom: str | None = None,
    ) -> dict[str, Any]:
        """Crée une ordonnance anesthésique via erp-connector.

        Args:
            animal_id: ID de l'animal (doit être numérique dans VetoPartner)
            surgery: Chirurgie avec doses calculées
            veto_id: ID du vétérinaire (optionnel)
            veto_nom: Nom du vétérinaire (optionnel)

        Returns:
            Dict avec status et détails de l'ordonnance créée.
        """
        # Valider les médicaments en stock
        valid, validation_msg = await cls.validate_anesthetic_prescription(surgery)
        if not valid:
            return {
                "success": False,
                "error": validation_msg,
                "ordonnance_id": None,
            }

        # Construire les lignes d'ordonnance
        lignes = []
        for dose in surgery.doses:
            # Chercher le produit pour obtenir son ID
            product = await cls.check_medicine_in_stock(dose.commercial_name)
            idsource = None
            if product:
                idsource = product.get("id") or product.get("idsource")

            ligne = {
                "designation": dose.commercial_name,
                "quantite": 1,
                "notes": f"{dose.dose_mg:.2f}mg ({dose.volume_ml:.2f}mL) - {dose.route} - {dose.phase}",
                "delivered": 0,  # Prescription uniquement, pas encore délivré
                "categorie": "MED",
                "idsource": idsource,
            }
            lignes.append(ligne)

        # Créer l'ordonnance via erp-connector
        try:
            async with httpx.AsyncClient(timeout=cls.TIMEOUT) as client:
                # animal_id doit être numérique pour erp-connector
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
                result = response.json()

                return {
                    "success": True,
                    "ordonnance_id": result.get("id") or result.get("ordonnance_id"),
                    "surgery_id": surgery.id,
                    "animal_id": animal_id,
                    "lignes_count": len(lignes),
                    "validation": validation_msg,
                }
        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Failed to create ordonnance: {e}")
            return {
                "success": False,
                "error": f"Erreur lors de la création de l'ordonnance: {str(e)}",
                "ordonnance_id": None,
            }
