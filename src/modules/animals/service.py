"""Service de gestion des animaux."""

from src.models import Animal

# Store en mémoire (remplacer par DB en production)
_animals_db: dict[str, Animal] = {}


class AnimalService:
    """Service pour gérer les animaux."""

    @staticmethod
    def create_animal(animal_id: str, animal: Animal) -> Animal:
        """Crée un nouvel animal.

        Args:
            animal_id: ID unique de l'animal
            animal: Données de l'animal

        Returns:
            L'animal créé.
        """
        animal_data = animal.model_dump()
        animal_data["id"] = animal_id
        stored = Animal(**animal_data)
        _animals_db[animal_id] = stored
        return stored

    @staticmethod
    def get_animal(animal_id: str) -> Animal | None:
        """Récupère un animal par ID.

        Args:
            animal_id: ID de l'animal

        Returns:
            L'animal ou None.
        """
        return _animals_db.get(animal_id)

    @staticmethod
    def list_animals() -> list[Animal]:
        """Liste tous les animaux.

        Returns:
            Liste des animaux.
        """
        return list(_animals_db.values())

    @staticmethod
    def update_animal(animal_id: str, animal: Animal) -> Animal | None:
        """Met à jour un animal.

        Args:
            animal_id: ID de l'animal
            animal: Nouvelles données

        Returns:
            L'animal mis à jour ou None.
        """
        if animal_id not in _animals_db:
            return None
        animal_data = animal.model_dump()
        animal_data["id"] = animal_id
        stored = Animal(**animal_data)
        _animals_db[animal_id] = stored
        return stored

    @staticmethod
    def delete_animal(animal_id: str) -> bool:
        """Supprime un animal.

        Args:
            animal_id: ID de l'animal

        Returns:
            True si supprimé, False si non trouvé.
        """
        if animal_id in _animals_db:
            del _animals_db[animal_id]
            return True
        return False
