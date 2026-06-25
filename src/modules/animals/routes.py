"""Routes FastAPI pour les animaux."""

from typing import Any

from fastapi import APIRouter

from src.models import Animal
from src.modules.animals.service import AnimalService

router = APIRouter(prefix="/api/animals", tags=["animals"])


@router.post("/")
async def create_animal(animal_id: str, animal: Animal) -> Animal:
    """Crée un nouvel animal.

    Args:
        animal_id: ID unique de l'animal
        animal: Données de l'animal

    Returns:
        L'animal créé.
    """
    return AnimalService.create_animal(animal_id, animal)


@router.get("/")
async def list_animals() -> list[Animal]:
    """Liste tous les animaux."""
    return AnimalService.list_animals()


@router.get("/{animal_id}")
async def get_animal(animal_id: str) -> dict[str, Any]:
    """Récupère un animal par ID.

    Args:
        animal_id: ID de l'animal

    Returns:
        Données de l'animal ou erreur 404.
    """
    animal = AnimalService.get_animal(animal_id)
    if not animal:
        return {"error": "Animal not found", "status": 404}
    return animal.model_dump()


@router.put("/{animal_id}")
async def update_animal(animal_id: str, animal: Animal) -> dict[str, Any]:
    """Met à jour un animal.

    Args:
        animal_id: ID de l'animal
        animal: Nouvelles données

    Returns:
        Données mises à jour ou erreur 404.
    """
    updated = AnimalService.update_animal(animal_id, animal)
    if not updated:
        return {"error": "Animal not found", "status": 404}
    return updated.model_dump()


@router.delete("/{animal_id}")
async def delete_animal(animal_id: str) -> dict[str, Any]:
    """Supprime un animal.

    Args:
        animal_id: ID de l'animal

    Returns:
        Status de suppression.
    """
    deleted = AnimalService.delete_animal(animal_id)
    return {"deleted": deleted, "animal_id": animal_id}
