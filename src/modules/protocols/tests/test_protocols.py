"""Tests unitaires pour ProtocolService."""

from src.modules.protocols.service import ProtocolService


def test_load_protocols() -> None:
    """Test loading protocols from JSON."""
    protocols = ProtocolService.load_protocols()
    assert len(protocols) > 0
    assert protocols[0].id


def test_get_protocol() -> None:
    """Test getting a specific protocol."""
    protocol = ProtocolService.get_protocol("mk_standard")
    assert protocol is not None
    assert protocol.id == "mk_standard"
    assert len(protocol.drugs) > 0


def test_get_protocol_not_found() -> None:
    """Test getting a non-existent protocol."""
    protocol = ProtocolService.get_protocol("nonexistent")
    assert protocol is None


def test_get_protocols_by_species() -> None:
    """Test filtering protocols by species."""
    dog_protocols = ProtocolService.get_protocols_for_species("chien")
    assert len(dog_protocols) > 0

    cat_protocols = ProtocolService.get_protocols_for_species("chat")
    assert len(cat_protocols) > 0


def test_calculate_dose() -> None:
    """Test dose calculation."""
    result = ProtocolService.calculate_dose("mk_standard", 20.0)
    assert result is not None
    assert result["weight_kg"] == 20.0
    assert "doses" in result
    assert len(result["doses"]) > 0

    # Check first dose
    dose = result["doses"][0]
    assert "drug_name" in dose
    assert "dose_mg" in dose
    assert "volume_ml" in dose
    assert dose["dose_mg"] > 0
    assert dose["volume_ml"] > 0


def test_calculate_dose_invalid_protocol() -> None:
    """Test dose calculation with invalid protocol."""
    result = ProtocolService.calculate_dose("invalid", 20.0)
    assert result is None
