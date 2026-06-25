"""Tests unitaires pour SurgeryService."""

from src.modules.surgeries.service import SurgeryService


def test_create_surgery() -> None:
    """Test creating a surgery."""
    surgery = SurgeryService.create_surgery(
        surgery_id="surg_001",
        animal_id="dog_001",
        protocol_id="mk_standard",
        weight_kg=20.0,
        vet_id="vet_001",
    )
    assert surgery is not None
    assert surgery.id == "surg_001"
    assert surgery.animal_id == "dog_001"
    assert surgery.protocol_id == "mk_standard"
    assert len(surgery.doses) > 0
    assert surgery.status == "draft"


def test_create_surgery_invalid_protocol() -> None:
    """Test creating surgery with invalid protocol."""
    surgery = SurgeryService.create_surgery(
        surgery_id="surg_invalid",
        animal_id="dog_001",
        protocol_id="nonexistent",
        weight_kg=20.0,
    )
    assert surgery is None


def test_get_surgery() -> None:
    """Test retrieving a surgery."""
    SurgeryService.create_surgery(
        surgery_id="surg_get",
        animal_id="dog_001",
        protocol_id="mk_standard",
        weight_kg=20.0,
    )
    surgery = SurgeryService.get_surgery("surg_get")
    assert surgery is not None
    assert surgery.id == "surg_get"


def test_get_surgery_not_found() -> None:
    """Test retrieving a non-existent surgery."""
    surgery = SurgeryService.get_surgery("nonexistent")
    assert surgery is None


def test_list_surgeries() -> None:
    """Test listing all surgeries."""
    SurgeryService.create_surgery(
        surgery_id="surg_list1",
        animal_id="dog_list",
        protocol_id="mk_standard",
        weight_kg=20.0,
    )
    SurgeryService.create_surgery(
        surgery_id="surg_list2",
        animal_id="dog_list",
        protocol_id="sedation_legere",
        weight_kg=20.0,
    )
    surgeries = SurgeryService.list_surgeries()
    assert len(surgeries) >= 2


def test_list_surgeries_by_animal() -> None:
    """Test filtering surgeries by animal."""
    SurgeryService.create_surgery(
        surgery_id="surg_animal1",
        animal_id="dog_filter",
        protocol_id="mk_standard",
        weight_kg=20.0,
    )
    SurgeryService.create_surgery(
        surgery_id="surg_animal2",
        animal_id="dog_filter",
        protocol_id="sedation_legere",
        weight_kg=20.0,
    )

    surgeries = SurgeryService.list_surgeries(animal_id="dog_filter")
    assert len(surgeries) >= 2
    assert all(s.animal_id == "dog_filter" for s in surgeries)


def test_validate_surgery() -> None:
    """Test validating a surgery."""
    SurgeryService.create_surgery(
        surgery_id="surg_validate",
        animal_id="dog_001",
        protocol_id="mk_standard",
        weight_kg=20.0,
    )
    validated = SurgeryService.validate_surgery("surg_validate")
    assert validated is True

    surgery = SurgeryService.get_surgery("surg_validate")
    assert surgery is not None
    assert surgery.status == "validated"


def test_validate_nonexistent_surgery() -> None:
    """Test validating a non-existent surgery."""
    validated = SurgeryService.validate_surgery("nonexistent")
    assert validated is False


def test_update_surgery_notes() -> None:
    """Test updating surgery notes."""
    SurgeryService.create_surgery(
        surgery_id="surg_notes",
        animal_id="dog_001",
        protocol_id="mk_standard",
        weight_kg=20.0,
    )
    updated = SurgeryService.update_surgery_notes("surg_notes", "Test notes")
    assert updated is not None
    assert updated.notes == "Test notes"
