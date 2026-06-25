"""Configuration pytest pour verso-surgery."""

import pytest


@pytest.fixture
def sample_animal_data():
    """Fixture pour un animal de test."""
    return {
        "name": "TestDog",
        "species": "chien",
        "weight_kg": 25.0,
        "age_years": 3.0,
        "owner_name": "Jean",
    }


@pytest.fixture
def sample_surgery_data():
    """Fixture pour une chirurgie de test."""
    return {
        "animal_id": "test_animal",
        "protocol_id": "mk_standard",
        "weight_kg": 25.0,
        "vet_id": "vet_001",
    }
