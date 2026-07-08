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
