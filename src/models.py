"""Modèles de données pour verso-surgery."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class Animal(BaseModel):
    """Modèle animal."""

    id: str = Field(default="", description="ID de l'animal (défini par la route)")
    name: str
    species: str = Field(..., description="chien ou chat")
    weight_kg: float = Field(..., gt=0, description="Poids en kg")
    age_years: float = Field(default=1.0, ge=0)
    owner_name: str = ""


class Drug(BaseModel):
    """Modèle drogue anesthésique."""

    name: str
    commercial: str
    concentration: float
    unit: str
    dose: float
    dose_unit: str
    dose_min: float = 0.0
    dose_max: float = 0.0
    route: str
    phase: str
    optional: bool = False
    code_central: str | None = None


class Protocol(BaseModel):
    """Modèle protocole anesthésique."""

    id: str
    name: str
    description: str
    species: list[str]
    drugs: list[Drug]


class SurgeryDose(BaseModel):
    """Calcul de dose pour une drogue."""

    drug_name: str
    commercial_name: str
    dose_mg: float
    volume_ml: float
    dose_min: float = 0.0
    dose_max: float = 0.0
    volume_min_ml: float = 0.0
    volume_max_ml: float = 0.0
    route: str
    phase: str
    optional: bool = False
    code_central: str | None = None


class Surgery(BaseModel):
    """Modèle chirurgie."""

    id: str
    animal_id: str
    protocol_id: str
    weight_kg: float
    doses: list[SurgeryDose]
    vet_id: str = ""
    status: str = "draft"
    notes: str = ""


class OrdonnanceLigne(BaseModel):
    """Ligne d'ordonnance."""

    designation: str = Field(..., description="Nom du médicament")
    quantite: int = Field(default=1, description="Quantité")
    notes: str = Field(default="", description="Notes/posologie")
    type_ligne: str = Field(default="hors_stock", description="Type: produit, hors_stock, note")


class CreateConsultationRequest(BaseModel):
    """Requête création consultation."""

    animal_id: int
    synthese: str
    motif: str = "Chirurgie"
    veto_id: int | None = None
    site_id: int | None = None


class CreateOrdonnanceRequest(BaseModel):
    """Requête création ordonnance."""

    animal_id: int
    lignes: list[OrdonnanceLigne]
    veto_id: int | None = None
    site_id: int = 2


# ===== SUIVI MODULE =====


class StageStatus(StrEnum):
    """Statut d'une étape de suivi."""

    PENDING = "pending"
    DONE = "done"
    SKIPPED = "skipped"


class SuiviStageData(BaseModel):
    """Données d'une étape de suivi."""

    status: StageStatus = StageStatus.PENDING
    timestamp: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)


class SuiviTracking(BaseModel):
    """État de suivi d'un rendez-vous."""

    appointment_id: str
    animal_id: int
    animal_nom: str
    espece: str
    poids_kg: float
    client_nom: str
    client_prenom: str
    vet_id: int | None = None
    site_id: int = 2
    date_rdv: str
    created_at: str
    updated_at: str
    current_stage: str = "arrivee"
    stages: dict[str, SuiviStageData] = Field(default_factory=dict)


class SuiviDrug(BaseModel):
    """Médicament dans protocole suivi."""

    name: str
    commercial: str
    concentration: float
    unit: str
    dose: float
    dose_unit: str
    dose_min: float = 0.0
    dose_max: float = 0.0
    route: str
    phase: str
    optional: bool = False
    code_central: str | None = None


class ProtocolSuivi(BaseModel):
    """Protocole anesthésique pour suivi."""

    id: str
    name: str
    description: str
    species: list[str]
    drugs: list[SuiviDrug]


class ArriveRequest(BaseModel):
    """Requête étape 1 — Arrivée."""

    appointment_id: str
    animal_id: int
    animal_nom: str
    espece: str
    poids_kg: float
    client_nom: str
    client_prenom: str
    vet_id: int | None = None
    site_id: int = 2
    date_rdv: str


class AnesthesieRequest(BaseModel):
    """Requête étape 2 — Anesthésie."""

    appointment_id: str
    protocol_id: str
    poids_kg: float
    doses: list[dict[str, Any]]
    veto_id: int | None = None
    site_id: int = 2
    skip_ordonnance: bool = False


class ActesRequest(BaseModel):
    """Requête étape 3 — Actes/Soins."""

    appointment_id: str
    actes: list[dict[str, Any]]


class SortieRequest(BaseModel):
    """Requête étape 4 — Sortie consultation."""

    appointment_id: str
    synthese: str
    veto_id: int | None = None
    site_id: int = 2
