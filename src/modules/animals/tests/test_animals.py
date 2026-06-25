"""Tests unitaires pour AnimalService."""

from src.models import Animal
from src.modules.animals.service import AnimalService


def test_create_animal() -> None:
    """Test creating an animal."""
    animal_data = Animal(
        id="",
        name="Rex",
        species="chien",
        weight_kg=25.0,
        age_years=3.0,
        owner_name="Jean",
    )
    animal = AnimalService.create_animal("dog_001", animal_data)
    assert animal.id == "dog_001"
    assert animal.name == "Rex"
    assert animal.weight_kg == 25.0


def test_get_animal() -> None:
    """Test retrieving an animal."""
    animal_data = Animal(
        id="",
        name="Minou",
        species="chat",
        weight_kg=4.5,
        age_years=2.0,
        owner_name="Marie",
    )
    AnimalService.create_animal("cat_001", animal_data)
    retrieved = AnimalService.get_animal("cat_001")
    assert retrieved is not None
    assert retrieved.name == "Minou"


def test_get_animal_not_found() -> None:
    """Test retrieving a non-existent animal."""
    animal = AnimalService.get_animal("nonexistent")
    assert animal is None


def test_list_animals() -> None:
    """Test listing all animals."""
    # Create some test animals
    animal1 = Animal(
        id="",
        name="Dog1",
        species="chien",
        weight_kg=20.0,
        age_years=1.0,
        owner_name="Owner1",
    )
    animal2 = Animal(
        id="",
        name="Cat1",
        species="chat",
        weight_kg=5.0,
        age_years=2.0,
        owner_name="Owner2",
    )
    AnimalService.create_animal("test_dog", animal1)
    AnimalService.create_animal("test_cat", animal2)

    animals = AnimalService.list_animals()
    assert len(animals) >= 2


def test_update_animal() -> None:
    """Test updating an animal."""
    original = Animal(
        id="",
        name="Buddy",
        species="chien",
        weight_kg=30.0,
        age_years=5.0,
        owner_name="Bob",
    )
    AnimalService.create_animal("dog_update", original)

    updated_data = Animal(
        id="",
        name="BuddyUpdated",
        species="chien",
        weight_kg=31.0,
        age_years=6.0,
        owner_name="Bob",
    )
    updated = AnimalService.update_animal("dog_update", updated_data)
    assert updated is not None
    assert updated.name == "BuddyUpdated"
    assert updated.weight_kg == 31.0


def test_delete_animal() -> None:
    """Test deleting an animal."""
    animal_data = Animal(
        id="",
        name="ToDelete",
        species="chien",
        weight_kg=20.0,
        age_years=1.0,
        owner_name="Test",
    )
    AnimalService.create_animal("dog_delete", animal_data)

    deleted = AnimalService.delete_animal("dog_delete")
    assert deleted is True

    retrieved = AnimalService.get_animal("dog_delete")
    assert retrieved is None
