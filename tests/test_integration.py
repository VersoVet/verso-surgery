"""Tests d'intégration pour verso-surgery."""

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_health():
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["service"] == "verso-surgery"


def test_ready():
    """Test readiness endpoint."""
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert "ready" in data


def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "verso-surgery"
    assert "endpoints" in data


def test_list_protocols():
    """Test listing protocols."""
    response = client.get("/api/protocols/")
    assert response.status_code == 200
    protocols = response.json()
    assert len(protocols) > 0
    assert protocols[0]["id"]


def test_get_protocol():
    """Test getting a specific protocol."""
    response = client.get("/api/protocols/mk_standard")
    assert response.status_code == 200
    protocol = response.json()
    assert protocol["id"] == "mk_standard"
    assert "drugs" in protocol


def test_protocols_by_species():
    """Test filtering protocols by species."""
    response = client.get("/api/protocols/species/chien")
    assert response.status_code == 200
    protocols = response.json()
    assert len(protocols) > 0


def test_calculate_doses():
    """Test dose calculation."""
    response = client.post("/api/protocols/doses/mk_standard?weight_kg=20")
    assert response.status_code == 200
    result = response.json()
    assert result["weight_kg"] == 20
    assert "doses" in result
    assert len(result["doses"]) > 0


def test_create_animal():
    """Test creating an animal."""
    response = client.post(
        "/api/animals/?animal_id=test_dog",
        json={
            "name": "Rex",
            "species": "chien",
            "weight_kg": 25.0,
            "age_years": 3.0,
            "owner_name": "Jean",
        },
    )
    assert response.status_code == 200
    animal = response.json()
    assert animal["id"] == "test_dog"
    assert animal["name"] == "Rex"


def test_list_animals():
    """Test listing animals."""
    # Create one first
    client.post(
        "/api/animals/?animal_id=test_cat",
        json={
            "name": "Minou",
            "species": "chat",
            "weight_kg": 4.5,
            "age_years": 2.0,
            "owner_name": "Marie",
        },
    )
    response = client.get("/api/animals/")
    assert response.status_code == 200
    animals = response.json()
    assert len(animals) >= 1


def test_get_animal():
    """Test getting a specific animal."""
    client.post(
        "/api/animals/?animal_id=test_dog2",
        json={
            "name": "Buddy",
            "species": "chien",
            "weight_kg": 30.0,
            "age_years": 5.0,
            "owner_name": "Bob",
        },
    )
    response = client.get("/api/animals/test_dog2")
    assert response.status_code == 200
    animal = response.json()
    assert animal["name"] == "Buddy"


def test_create_surgery():
    """Test creating a surgery with dose calculation."""
    # Create animal first
    client.post(
        "/api/animals/?animal_id=surg_test_dog",
        json={
            "name": "TestDog",
            "species": "chien",
            "weight_kg": 20.0,
            "age_years": 3.0,
            "owner_name": "Test",
        },
    )

    response = client.post(
        "/api/surgeries/?surgery_id=surg_001&animal_id=surg_test_dog"
        "&protocol_id=mk_standard&weight_kg=20.0&vet_id=vet_001"
    )
    assert response.status_code == 200
    surgery = response.json()
    assert surgery["id"] == "surg_001"
    assert surgery["animal_id"] == "surg_test_dog"
    assert surgery["protocol_id"] == "mk_standard"
    assert "doses" in surgery
    assert len(surgery["doses"]) > 0


def test_get_surgery():
    """Test getting a surgery."""
    # Create surgery first
    client.post(
        "/api/animals/?animal_id=surg_test_dog2",
        json={
            "name": "TestDog2",
            "species": "chien",
            "weight_kg": 25.0,
            "age_years": 2.0,
            "owner_name": "Test2",
        },
    )

    client.post("/api/surgeries/?surgery_id=surg_002&animal_id=surg_test_dog2&protocol_id=mk_standard&weight_kg=25.0")

    response = client.get("/api/surgeries/surg_002")
    assert response.status_code == 200
    surgery = response.json()
    assert surgery["id"] == "surg_002"


def test_validate_surgery():
    """Test validating a surgery."""
    # Create surgery first
    client.post(
        "/api/animals/?animal_id=surg_test_dog3",
        json={
            "name": "TestDog3",
            "species": "chien",
            "weight_kg": 22.0,
            "age_years": 4.0,
            "owner_name": "Test3",
        },
    )

    client.post("/api/surgeries/?surgery_id=surg_003&animal_id=surg_test_dog3&protocol_id=mk_standard&weight_kg=22.0")

    response = client.post("/api/surgeries/surg_003/validate")
    assert response.status_code == 200
    result = response.json()
    assert result["validated"] is True
