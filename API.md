# API — verso-surgery

Base URL: `http://10.0.0.13:8112`

## Health & Status

### GET /health
Health check du service.

**Réponse**:
```json
{
  "status": "healthy",
  "service": "verso-surgery",
  "version": "0.1.12"
}
```

### GET /ready
Readiness check (pour Kubernetes/systemd).

**Réponse**:
```json
{
  "ready": true,
  "service": "verso-surgery"
}
```

### GET /
Informations du service.

**Réponse**:
```json
{
  "service": "verso-surgery",
  "description": "Gestion des chirurgies vétérinaires",
  "endpoints": {
    "health": "/health",
    "ready": "/ready",
    "protocols": "/api/protocols",
    "animals": "/api/animals",
    "surgeries": "/api/surgeries"
  }
}
```

---

## Dashboard (ErpPatientSelector)

Endpoints pour la sélection patient/RDV via la lib `erp-ui-sdk`.

### GET /api/dashboard/sites
Liste tous les sites vétérinaires depuis erp-connector.

**Réponse**:
```json
{
  "sites": [
    {
      "id": 1,
      "nom": "Clinique Principale",
      "adresse": "123 Rue Test",
      "telephone": "",
      "email": ""
    }
  ]
}
```

### GET /api/dashboard/vets
Liste tous les vétérinaires depuis erp-connector (filtrés, triés par nom).

**Réponse**:
```json
{
  "vets": [
    {
      "id": 12,
      "nom": "DUPONT",
      "prenom": "Jean",
      "email": "jean@test.com",
      "specialite": ""
    }
  ]
}
```

### GET /api/dashboard/appointments
Liste les RDV pour une plage de dates depuis erp-connector.

**Paramètres**:
- `date_from` (query): Date début (YYYY-MM-DD)
- `date_to` (query): Date fin (YYYY-MM-DD)
- `vet_id` (query, optionnel): Filtre par ID vétérinaire

**Exemple**:
```bash
curl "http://10.0.0.13:8112/api/dashboard/appointments?date_from=2026-07-04&date_to=2026-07-04&vet_id=12"
```

**Réponse**:
```json
{
  "appointments": [
    {
      "id": 1,
      "animal_id": 42,
      "animal_nom": "Fido",
      "espece": "chien",
      "race": "Labrador",
      "client_id": 100,
      "client_nom": "Dupont",
      "client_prenom": "Jean",
      "motif": "Consultation",
      "datetime_consult": "2026-07-04 14:30:00",
      "date_rdv": "2026-07-04",
      "vet_id": 12,
      "vet_name": "DUPONT",
      "duree_min": 30,
      "notes": ""
    }
  ]
}
```

---

## Protocoles Anesthésiques

### GET /api/protocols/
Liste tous les protocoles anesthésiques disponibles.

**Réponse**:
```json
[
  {
    "id": "sedation_legere",
    "name": "Sédation Légère",
    "description": "Pour examens courts, pansements",
    "species": ["chien", "chat"],
    "drugs": [
      {
        "name": "Médétomidine",
        "commercial": "Domitor",
        "concentration": 1.0,
        "unit": "mg/mL",
        "dose": 0.015,
        "dose_unit": "mg/kg",
        "route": "IM",
        "phase": "prémédication"
      }
    ]
  }
]
```

### GET /api/protocols/{protocol_id}
Récupère un protocole spécifique.

**Paramètres**:
- `protocol_id` (path): ID du protocole (ex: `mk_standard`)

**Réponse** (200):
```json
{
  "id": "mk_standard",
  "name": "MK Standard",
  "description": "Médétomidine + Kétamine — chirurgie courte/moyenne",
  "species": ["chien", "chat"],
  "drugs": [...]
}
```

**Erreur** (404):
```json
{
  "error": "Protocol not found",
  "status": 404
}
```

### GET /api/protocols/species/{species}
Liste les protocoles pour une espèce.

**Paramètres**:
- `species` (path): `chien` ou `chat`

**Réponse** (200):
```json
[
  {
    "id": "mk_standard",
    "name": "MK Standard",
    ...
  }
]
```

### POST /api/protocols/doses/{protocol_id}
Calcule les doses pour un protocole et poids.

**Paramètres**:
- `protocol_id` (path): ID du protocole
- `weight_kg` (query): Poids de l'animal en kg

**Exemple**:
```bash
curl -X POST "http://10.0.0.13:8112/api/protocols/doses/mk_standard?weight_kg=20"
```

**Réponse** (200):
```json
{
  "protocol_id": "mk_standard",
  "protocol_name": "MK Standard",
  "weight_kg": 20,
  "doses": [
    {
      "drug_name": "Médétomidine",
      "commercial_name": "Domitor",
      "dose_mg": 0.4,
      "volume_ml": 0.4,
      "route": "IM",
      "phase": "prémédication",
      "concentration": 1.0,
      "unit": "mg/mL"
    },
    {
      "drug_name": "Kétamine",
      "commercial_name": "Imalgène 1000",
      "dose_mg": 100.0,
      "volume_ml": 1.0,
      "route": "IM",
      "phase": "induction",
      "concentration": 100.0,
      "unit": "mg/mL"
    }
  ]
}
```

**Erreur** (404):
```json
{
  "error": "Protocol not found",
  "status": 404
}
```

---

## Animaux

### POST /api/animals/
Crée un nouvel animal.

**Paramètres**:
- `animal_id` (query): ID unique de l'animal
- Body (JSON):
  ```json
  {
    "name": "Rex",
    "species": "chien",
    "weight_kg": 25.5,
    "age_years": 3.5,
    "owner_name": "Jean"
  }
  ```

**Exemple**:
```bash
curl -X POST "http://10.0.0.13:8112/api/animals/?animal_id=dog_001" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Rex",
    "species": "chien",
    "weight_kg": 25.5,
    "age_years": 3.5,
    "owner_name": "Jean"
  }'
```

**Réponse** (200):
```json
{
  "id": "dog_001",
  "name": "Rex",
  "species": "chien",
  "weight_kg": 25.5,
  "age_years": 3.5,
  "owner_name": "Jean"
}
```

### GET /api/animals/
Liste tous les animaux.

**Réponse** (200):
```json
[
  {
    "id": "dog_001",
    "name": "Rex",
    "species": "chien",
    "weight_kg": 25.5,
    "age_years": 3.5,
    "owner_name": "Jean"
  }
]
```

### GET /api/animals/{animal_id}
Récupère les détails d'un animal.

**Paramètres**:
- `animal_id` (path): ID de l'animal

**Réponse** (200):
```json
{
  "id": "dog_001",
  "name": "Rex",
  "species": "chien",
  "weight_kg": 25.5,
  "age_years": 3.5,
  "owner_name": "Jean"
}
```

**Erreur** (404):
```json
{
  "error": "Animal not found",
  "status": 404
}
```

### PUT /api/animals/{animal_id}
Met à jour un animal.

**Paramètres**:
- `animal_id` (path): ID de l'animal
- Body (JSON): Même structure que POST

**Réponse** (200): Données mises à jour

**Erreur** (404): Animal non trouvé

### DELETE /api/animals/{animal_id}
Supprime un animal.

**Paramètres**:
- `animal_id` (path): ID de l'animal

**Réponse** (200):
```json
{
  "deleted": true,
  "animal_id": "dog_001"
}
```

---

## Chirurgies

### POST /api/surgeries/
Crée une nouvelle chirurgie avec calcul des doses.

**Paramètres**:
- `surgery_id` (query): ID unique de la chirurgie
- `animal_id` (query): ID de l'animal
- `protocol_id` (query): ID du protocole anesthésique
- `weight_kg` (query): Poids de l'animal (pour validation)
- `vet_id` (query, optionnel): ID du vétérinaire

**Exemple**:
```bash
curl -X POST "http://10.0.0.13:8112/api/surgeries/" \
  -H "Content-Type: application/json" \
  -d '{
    "surgery_id": "surg_001",
    "animal_id": "dog_001",
    "protocol_id": "mk_standard",
    "weight_kg": 25.5,
    "vet_id": "vet_12"
  }'
```

**Réponse** (200):
```json
{
  "id": "surg_001",
  "animal_id": "dog_001",
  "protocol_id": "mk_standard",
  "weight_kg": 25.5,
  "doses": [
    {
      "drug_name": "Médétomidine",
      "commercial_name": "Domitor",
      "dose_mg": 0.51,
      "volume_ml": 0.51,
      "route": "IM",
      "phase": "prémédication"
    },
    {
      "drug_name": "Kétamine",
      "commercial_name": "Imalgène 1000",
      "dose_mg": 127.5,
      "volume_ml": 1.28,
      "route": "IM",
      "phase": "induction"
    },
    {
      "drug_name": "Butorphanol",
      "commercial_name": "Torbugesic",
      "dose_mg": 7.65,
      "volume_ml": 0.77,
      "route": "IM",
      "phase": "analgésie"
    }
  ],
  "vet_id": "vet_12",
  "status": "draft",
  "notes": ""
}
```

**Erreur** (404):
```json
{
  "error": "Protocol not found",
  "status": 404
}
```

### GET /api/surgeries/{surgery_id}
Récupère les détails d'une chirurgie.

**Paramètres**:
- `surgery_id` (path): ID de la chirurgie

**Réponse** (200): Données de la chirurgie

**Erreur** (404): Chirurgie non trouvée

### GET /api/surgeries/
Liste les chirurgies (optionnellement filtrées par animal).

**Paramètres**:
- `animal_id` (query, optionnel): Filtre par animal

**Exemple**:
```bash
# Toutes les chirurgies
curl "http://10.0.0.13:8112/api/surgeries/"

# Chirurgies pour un animal
curl "http://10.0.0.13:8112/api/surgeries/?animal_id=dog_001"
```

**Réponse** (200):
```json
[
  {
    "id": "surg_001",
    "animal_id": "dog_001",
    "protocol_id": "mk_standard",
    "weight_kg": 25.5,
    "doses": [...],
    "vet_id": "vet_12",
    "status": "draft",
    "notes": ""
  }
]
```

### POST /api/surgeries/{surgery_id}/validate
Valide une chirurgie (change status à "validated").

**Paramètres**:
- `surgery_id` (path): ID de la chirurgie

**Réponse** (200):
```json
{
  "validated": true,
  "surgery_id": "surg_001"
}
```

**Erreur** (404): Chirurgie non trouvée

### PUT /api/surgeries/{surgery_id}/notes
Met à jour les notes d'une chirurgie.

**Paramètres**:
- `surgery_id` (path): ID de la chirurgie
- `notes` (query): Nouvelles notes

**Exemple**:
```bash
curl -X PUT "http://10.0.0.13:8112/api/surgeries/surg_001/notes?notes=Animal%20calme%2C%20bon%20champ%20op"
```

**Réponse** (200): Chirurgie mise à jour

**Erreur** (404): Chirurgie non trouvée

---

## Ordonnances Anesthésiques (intégration erp-connector)

### POST /api/prescriptions/{surgery_id}/create-ordonnance
Crée une ordonnance anesthésique dans VetoPartner via erp-connector (v1.8.153+).

Utilise la nouvelle API erp-connector avec `code_central` et auto-enrichissement:
- Cherche les codes centraux pour les médicaments
- Les lignes avec code_central sont créées avec auto-remplissage de `designation` et `CIP`
- Les lignes sans code_central sont créées comme "hors_stock" avec le nom du médicament
- `delivered` et autres champs sont auto-définis par erp-connector

**Paramètres**:
- `surgery_id` (path): ID de la chirurgie (avec doses calculées)
- `animal_id` (query): ID de l'animal (numérique, correspond à l'ID VetoPartner)
- `veto_id` (query, optionnel): ID du vétérinaire
- `veto_nom` (query, optionnel): Nom du vétérinaire

**Exemple**:
```bash
curl -X POST "http://10.0.0.44:8112/api/prescriptions/surg_001/create-ordonnance?animal_id=42&veto_id=1&veto_nom=Dr%20Martin"
```

**Réponse** (200):
```json
{
  "success": true,
  "ordonnance_id": 12345,
  "surgery_id": "surg_001",
  "animal_id": "42",
  "lignes_count": 3,
  "message": "Ordonnance créée (3 lignes)"
}
```

**Erreur** (200 avec success=false):
```json
{
  "success": false,
  "error": "animal_id doit être numérique: abc",
  "ordonnance_id": null
}
```

**Notes**:
- Les codes centraux sont recherchés automatiquement dans le catalogue VetoPartner
- Médicaments non trouvés: créés comme "hors_stock" pour permettre édition manuelle dans VetoPartner
- Ordonnance toujours créée en tant que "prescription uniquement" (type_ordo=1)
- Voir erp-connector API.md pour détails sur `code_central`, `type_ligne`, auto-enrichissement

---

## Codes de réponse

- **200 OK**: Requête réussie
- **404 Not Found**: Ressource non trouvée
- **422 Unprocessable Entity**: Validation Pydantic échouée
- **500 Internal Server Error**: Erreur serveur

---

## Authentification & Sécurité

- ⚠️ Pas d'authentification actuellement (à ajouter: OAuth, session)
- ⚠️ Store en mémoire (perte au redémarrage)
- À faire: JWT/session vétérinaire pour vet_id

---

## Futurs endpoints

- `GET /surgeries/{id}/pdf` ← export PDF anesthésique
- Redis pubsub sur `surgery:validated` ← notifications
- `PATCH /animals/{id}` ← sync avec VetoPartner
