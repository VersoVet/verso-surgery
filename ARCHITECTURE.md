# Architecture — verso-surgery

## Vue d'ensemble

Verso Surgery est un service FastAPI pour la gestion des chirurgies vétérinaires avec calcul automatique des doses anesthésiques.

```
Client (Frontend/API)
    ↓
FastAPI (port 8112)
    ├── /api/protocols → ProtocolService (JSON statique)
    ├── /api/animals   → AnimalService (store mémoire)
    └── /api/surgeries → SurgeryService (protocole + doses)
```

## Structure Modules

### 1. **protocols** — Protocoles anesthésiques

- **Service**: `ProtocolService`
  - Charge les 5 protocoles depuis `protocols.json`
  - Calcule les doses pour un animal/protocole
  - Cache les protocoles en mémoire

- **Routes**:
  - `GET /api/protocols/` — Tous les protocoles
  - `GET /api/protocols/{id}` — Détails protocole
  - `GET /api/protocols/species/{species}` — Protocoles pour espèce
  - `POST /api/protocols/doses/{id}` — Calcul doses

### 2. **animals** — Gestion des animaux

- **Service**: `AnimalService`
  - CRUD simple pour les animaux
  - Store en mémoire (à remplacer par DB)
  - Validation Pydantic

- **Routes**:
  - `POST /api/animals/` — Créer animal
  - `GET /api/animals/` — Lister tous
  - `GET /api/animals/{id}` — Détails
  - `PUT /api/animals/{id}` — Mettre à jour
  - `DELETE /api/animals/{id}` — Supprimer

### 3. **surgeries** — Gestion des chirurgies

- **Service**: `SurgeryService`
  - Crée chirurgies avec calcul des doses
  - Lie animal + protocole
  - Historique par animal
  - Store en mémoire (à remplacer par DB)

- **Routes**:
  - `POST /api/surgeries/` — Créer chirurgie
  - `GET /api/surgeries/{id}` — Détails
  - `GET /api/surgeries/` — Lister (avec filtre animal_id)
  - `POST /api/surgeries/{id}/validate` — Valider
  - `PUT /api/surgeries/{id}/notes` — Ajouter notes

## Points d'entrée

### Health Checks

- `GET /health` → `{"status": "healthy/degraded", ...}`
- `GET /ready` → `{"ready": true/false, ...}`

### Main

- `GET /` → Informations service

## Modèles de données

### Animal
```python
- id: str
- name: str
- species: "chien" | "chat"
- weight_kg: float
- age_years: float
- owner_name: str
```

### Protocol
```python
- id: str
- name: str
- description: str
- species: list[str]
- drugs: list[Drug]
```

### Surgery
```python
- id: str
- animal_id: str
- protocol_id: str
- weight_kg: float
- doses: list[SurgeryDose]
- vet_id: str
- status: "draft" | "validated"
- notes: str
```

## Lifespan & Démarrage

1. Charge les 5 protocoles depuis `protocols.json` (cache)
2. Vérifie que les protocoles sont disponibles
3. Marque le service comme prêt
4. À l'arrêt, nettoie les ressources

## Limitations actuelles

- **Store**: En mémoire, perdus au redémarrage
  - À remplacer par SQLite/PostgreSQL
  
- **Auth**: Pas d'authentification
  - À ajouter: vet_id depuis session

- **Intégration ERP**: Pas implémentée
  - À faire: PATCH /animals/{id}, POST /animals/{id}/ordonnances vers erp-connector

- **Export**: Pas de PDF/export
  - À faire: générer fiches chirurgie

- **Notifications**: Pas de Redis
  - À faire: publier événements sur chirurgie validée

## Tailles de fichiers

- `src/main.py`: ~150 lignes ✓
- `src/models.py`: ~60 lignes ✓
- `src/modules/protocols/service.py`: ~75 lignes ✓
- `src/modules/animals/service.py`: ~60 lignes ✓
- `src/modules/surgeries/service.py`: ~80 lignes ✓
- Routes: <50 lignes chacune ✓

Tous les fichiers Python < 300 lignes (validations Forge).

## Qualité Code

- ✓ Types explicites (mypy)
- ✓ Docstrings Google convention
- ✓ Imports absolus (`from src.xxx`)
- ✓ Pas de credentials en dur
- ✓ httpx async pour HTTP
- ✓ Pydantic pour validation
- ✓ Linting Ruff + format
