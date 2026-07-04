"""Tests pour le module prescriptions."""

import pytest

from src.models import Surgery, SurgeryDose
from src.modules.prescriptions.service import PrescriptionService


@pytest.fixture
def sample_surgery() -> Surgery:
    """Fixture pour une chirurgie test."""
    return Surgery(
        id="test_001",
        animal_id="42",
        protocol_id="mk_standard",
        weight_kg=20.0,
        doses=[
            SurgeryDose(
                drug_name="Médétomidine",
                commercial_name="Domitor",
                dose_mg=0.3,
                volume_ml=0.3,
                route="IM",
                phase="prémédication",
            ),
            SurgeryDose(
                drug_name="Kétamine",
                commercial_name="Imalgène 1000",
                dose_mg=100.0,
                volume_ml=1.0,
                route="IM",
                phase="induction",
            ),
        ],
        vet_id="vet_12",
    )


def test_surgery_model(sample_surgery: Surgery) -> None:
    """Test le modèle Surgery."""
    assert sample_surgery.id == "test_001"
    assert sample_surgery.animal_id == "42"
    assert sample_surgery.weight_kg == 20.0
    assert len(sample_surgery.doses) == 2
    assert sample_surgery.doses[0].commercial_name == "Domitor"
    assert sample_surgery.doses[1].commercial_name == "Imalgène 1000"


def test_surgery_serialization(sample_surgery: Surgery) -> None:
    """Test la sérialisation d'une chirurgie."""
    data = sample_surgery.model_dump()
    assert data["id"] == "test_001"
    assert data["animal_id"] == "42"
    assert isinstance(data["doses"], list)
    assert len(data["doses"]) == 2


def test_prescription_service_exists() -> None:
    """Test que le service prescriptions est disponible."""
    assert hasattr(PrescriptionService, "create_ordonnance")
    assert hasattr(PrescriptionService, "search_product_by_code_central")
    assert hasattr(PrescriptionService, "search_product_by_designation")
