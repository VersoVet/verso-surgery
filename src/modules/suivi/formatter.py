"""Formatage du compte-rendu de consultation pour VetoPartner."""

from src.models import SuiviTracking


def format_consultation(tracking: SuiviTracking) -> str:
    """Formate la consultation de sortie avec sections structurées.

    Args:
        tracking: État de suivi complet du cas.

    Returns:
        Texte formaté avec CRLF pour VetoPartner.
    """
    CRLF = "\r\n"
    sections = []

    # En-tête
    header = (
        f"Patient: {tracking.animal_nom} ({tracking.espece}, {tracking.poids_kg} kg) "
        f"— {tracking.date_rdv}"
    )
    sections.append(header)

    # Anesthésie réalisée
    anesth_data = tracking.stages.get("anesthesie", {}).data
    if anesth_data and anesth_data.get("doses"):
        anesth_section = "ANESTHÉSIE RÉALISÉE:"
        protocol_name = anesth_data.get("protocol_name", "Protocole inconnu")
        anesth_section += f" {protocol_name}"

        for dose in anesth_data.get("doses", []):
            if dose.get("selected", True):
                volume = f"{dose.get('volume_ml', 0):.2f}"
                route = dose.get("route", "?")
                phase = dose.get("phase", "?")
                anesth_section += (
                    f"{CRLF}- {dose.get('commercial', '?')}: {volume} mL {route} — {phase}"
                )

        sections.append(anesth_section)

    # Actes réalisés
    actes_data = tracking.stages.get("actes", {}).data
    if actes_data and actes_data.get("actes"):
        actes_section = "ACTES RÉALISÉS:"
        for act in actes_data.get("actes", []):
            act_name = act.get("act_name", "Acte inconnu")
            actes_section += f"{CRLF}→ {act_name}"

            fields = act.get("fields", {})
            for field_id, value in fields.items():
                if value and value != "":
                    actes_section += f"{CRLF}  {field_id}: {value}"

        sections.append(actes_section)

    # Joindre les sections avec double CRLF
    return (CRLF + CRLF).join(sections)
