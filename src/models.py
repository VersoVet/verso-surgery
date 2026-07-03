"""Modèles de données pour verso-surgery."""

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
    route: str
    phase: str


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
    route: str
    phase: str


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
