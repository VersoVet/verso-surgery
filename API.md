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
- `site_id` (query, optionnel): Filtre par ID site

**Exemple**:
```bash
curl "http://10.0.0.13:8112/api/dashboard/appointments?date_from=2026-07-04&date_to=2026-07-04&site_id=2&vet_id=12"
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

### GET /api/dashboard/acts
Liste tous les actes chirurgicaux disponibles.

**Réponse**:
```json
{
  "acts": [
    {
      "id": "fluoroscopie",
      "name": "Fluoroscopie",
      "description": "Imaging fluoroscopique...",
      "fields": [
        {
          "id": "region",
          "label": "Région",
          "type": "select",
          "options": ["Anterieures", "Posterieures", ...]
        }
      ]
    }
  ]
}
```

### GET /api/dashboard/search
Recherche un patient/animal.

**Paramètres**:
- `q` (query): Terme de recherche (min. 2 caractères)

**Exemple**:
```bash
curl "http://10.0.0.13:8112/api/dashboard/search?q=fido"
```

**Réponse**:
```json
{
  "results": [...]
}
```

### GET /api/dashboard/animal/{animal_id}
Récupère les détails d'un animal.

**Paramètres**:
- `animal_id` (path): ID VetoPartner de l'animal

**Réponse**:
```json
{
  "id": 42,
  "nom": "Fido",
  "espece": "Chien",
  "race": "Labrador",
  "poids": 25.5,
  "age_years": 3,
  "sexe": "Mâle",
  "client_id": 100,
  "client_nom": "Dupont"
}
```

### POST /api/dashboard/consultation
Crée une consultation VetoPartner via erp-connector.

**Paramètres**:
- `animal_id` (query): ID de l'animal VetoPartner
- `synthese` (query): Synthèse/contenu de la consultation
- `motif` (query, défaut: "Chirurgie"): Motif de la consultation
- `veto_id` (query, optionnel): ID du vétérinaire
- `site_id` (query, optionnel): ID du site

**Exemple**:
```bash
curl -X POST "http://10.0.0.13:8112/api/dashboard/consultation" \
  -H "Content-Type: application/json" \
  -d '{
    "animal_id": 42,
    "synthese": "Consultation chirurgicale pour ablation kystes",
    "motif": "Chirurgie",
    "veto_id": 1,
    "site_id": 2
  }'
```

**Réponse** (200):
```json
{
  "success": true,
  "consultation_id": 5432,
  "animal_id": 42
}
```

**Erreur** (200 avec success=false):
```json
{
  "success": false,
  "error": "Erreur lors de création consultation: ...",
  "consultation_id": null
}
```

### POST /api/dashboard/ordonnance
Crée une ordonnance VetoPartner via erp-connector.

**Paramètres**:
- `animal_id` (query): ID de l'animal VetoPartner
- `lignes` (JSON body): Tableau des lignes d'ordonnance
- `veto_id` (query, optionnel): ID du vétérinaire
- `site_id` (query, défaut: 2): ID du site

**Structure d'une ligne**:
```json
{
  "designation": "Nom du médicament",
  "quantite": 1,
  "delivered": 1,
  "notes": "Posologie/instructions",
  "type_ligne": "hors_stock" | "produit" | "note"
}
```

**Exemple**:
```bash
curl -X POST "http://10.0.0.13:8112/api/dashboard/ordonnance" \
  -H "Content-Type: application/json" \
  -d '{
    "animal_id": 42,
    "lignes": [
      {
        "designation": "Propofol",
        "quantite": 1,
        "delivered": 1,
        "notes": "2.5 mL (100 mg/mL)",
        "type_ligne": "hors_stock"
      },
      {
        "designation": "Domitor",
        "quantite": 1,
        "delivered": 1,
        "notes": "0.4 mL (1 mg/mL)",
        "type_ligne": "hors_stock"
      }
    ],
    "veto_id": 1,
    "site_id": 2
  }'
```

**Réponse** (200):
```json
{
  "success": true,
  "ordonnance_id": 9876,
  "animal_id": 42
}
```

**Erreur** (200 avec success=false):
```json
{
  "success": false,
  "error": "Erreur lors de création ordonnance: ...",
  "ordonnance_id": null
}
```

---

## Suivi de Prise en Charge (Dashboard 4 étapes)

Module de suivi journalier avec état persisté en JSON. Workflow: Arrivée → Anesthésie → Actes → Sortie.

### GET /api/suivi/protocoles
Liste tous les protocoles anesthésiques suivi.

**Réponse**:
```json
{
  "protocoles": [
    {
      "id": "sedation_legere",
      "name": "Sédation légère",
      "description": "Examen, pansement, imagerie",
      "species": ["chien", "chat"],
      "drugs": [
        {
          "name": "Médétomidine",
          "commercial": "SEDATOR",
          "concentration": 1.0,
          "unit": "mg/mL",
          "dose": 0.015,
          "dose_unit": "mg/kg",
          "dose_min": 0.01,
          "dose_max": 0.04,
          "route": "IM",
          "phase": "prémédication",
          "optional": false,
          "code_central": "83453"
        }
      ]
    }
  ]
}
```

### GET /api/suivi/tracking
Liste les trackings du jour (persistés en JSON).

**Paramètres**:
- `date` (query, optionnel): Date au format YYYY-MM-DD (défaut: aujourd'hui)

**Exemple**:
```bash
curl "http://10.0.0.13:8112/api/suivi/tracking?date=2026-07-09"
```

**Réponse**:
```json
{
  "trackings": [
    {
      "appointment_id": "180117",
      "animal_id": 21923,
      "animal_nom": "REGLISSE",
      "espece": "Chien",
      "poids_kg": 8.5,
      "client_nom": "DUFOURMENTEL",
      "client_prenom": "",
      "date_rdv": "2026-07-09",
      "current_stage": "anesthesie",
      "stages": {
        "arrivee": {"status": "done", "timestamp": "...", "data": {}},
        "anesthesie": {"status": "done", "timestamp": "...", "data": {"protocol_id": "...", "doses": [...]}},
        "actes": {"status": "pending", "timestamp": null, "data": {}},
        "sortie": {"status": "pending", "timestamp": null, "data": {}}
      }
    }
  ],
  "date": "2026-07-09"
}
```

### GET /api/suivi/tracking/{appointment_id}
Récupère le tracking d'un rendez-vous spécifique.

**Paramètres**:
- `appointment_id` (path): ID du rendez-vous

**Réponse** (200):
```json
{
  "success": true,
  "tracking": { ... }
}
```

**Erreur** (404):
```json
{
  "detail": "Tracking not found"
}
```

### DELETE /api/suivi/tracking/{appointment_id}
Réinitialise/supprime le tracking d'un rendez-vous.

**Paramètres**:
- `appointment_id` (path): ID du rendez-vous

**Réponse** (200):
```json
{
  "success": true,
  "appointment_id": "180117"
}
```

### POST /api/suivi/arrivee
Étape 1 — Crée ou met à jour un tracking à l'arrivée.

**Body (JSON)**:
```json
{
  "appointment_id": "180117",
  "animal_id": 21923,
  "animal_nom": "REGLISSE",
  "espece": "Chien",
  "poids_kg": 8.5,
  "client_nom": "DUFOURMENTEL",
  "client_prenom": "",
  "vet_id": null,
  "site_id": 2,
  "date_rdv": "2026-07-09"
}
```

**Réponse** (200):
```json
{
  "success": true,
  "tracking": { ... }
}
```

### POST /api/suivi/anesthesie
Étape 2 — Sélectionne protocole et crée ordonnance dans VetoPartner.

**Body (JSON)**:
```json
{
  "appointment_id": "180117",
  "protocol_id": "sedation_profonde",
  "poids_kg": 8.5,
  "doses": [
    {
      "name": "Médétomidine",
      "commercial": "SEDATOR",
      "volume_ml": 0.13,
      "route": "IM",
      "phase": "prémédication",
      "selected": true,
      "code_central": "83453"
    }
  ],
  "veto_id": null,
  "site_id": 2
}
```

**Réponse** (200):
```json
{
  "success": true,
  "tracking": { ... },
  "ordonnance_id": 12345
}
```

**Erreur**:
```json
{
  "success": false,
  "error": "Ordonnance creation failed: ..."
}
```

### POST /api/suivi/actes
Étape 3 — Enregistre les actes chirurgicaux sélectionnés.

**Body (JSON)**:
```json
{
  "appointment_id": "180117",
  "actes": [
    {
      "act_name": "Onde de choc",
      "fields": {
        "localisation": "Épaule droite",
        "frequence": "4 Hz",
        "pression": "2.5 bar"
      }
    }
  ]
}
```

**Réponse** (200):
```json
{
  "success": true,
  "tracking": { ... }
}
```

### POST /api/suivi/sortie
Étape 4 — Crée la consultation VetoPartner avec compte-rendu.

**Body (JSON)**:
```json
{
  "appointment_id": "180117",
  "synthese": "Patient: REGLISSE (Chien, 8.5 kg) — 2026-07-09\r\n\r\nANESTHÉSIE RÉALISÉE: Sédation profonde\r\n- SEDATOR: 0.13 mL IM — prémédication\r\n\r\nACTES RÉALISÉS:\r\n→ Onde de choc (séance 1)\r\n  Localisation: Épaule droite",
  "veto_id": null,
  "site_id": 2
}
```

**Réponse** (200):
```json
{
  "success": true,
  "tracking": { ... },
  "consultation_id": 54321
}
```

**Erreur**:
```json
{
  "success": false,
  "error": "Consultation creation failed: HTTP 500: ..."
}
```

### GET /api/suivi/preview/{appointment_id}
Prévisualise le compte-rendu avant validation (sans créer la consultation).

**Paramètres**:
- `appointment_id` (path): ID du rendez-vous

**Réponse** (200):
```json
{
  "success": true,
  "preview": "Patient: REGLISSE (Chien, 8.5 kg) — 2026-07-09\r\n\r\nANESTHÉSIE RÉALISÉE: ..."
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

## Configuration (Admin Panel)

### GET /api/dashboard/config/{config_name}
Récupère le contenu d'un fichier de configuration JSON.

**Paramètres**:
- `config_name` (path): Nom du fichier (acts, protocols, protocoles_suivi, presets)

**Exemple**:
```bash
curl "http://10.0.0.44:8112/api/dashboard/config/acts"
```

**Réponse** (200):
```json
{
  "success": true,
  "config": "acts",
  "data": [
    {
      "id": "fluoroscopie_sedation",
      "name": "Fluoroscopie — Sédation",
      "icon": "📷",
      "description": "Imagerie sous sédation...",
      "fields": [...]
    }
  ]
}
```

### POST /api/dashboard/config/{config_name}
Sauvegarde un fichier de configuration JSON modifié.

**Paramètres**:
- `config_name` (path): Nom du fichier (acts, protocols, protocoles_suivi, presets)
- Body: `{ "data": {...} }`

**Exemple**:
```bash
curl -X POST "http://10.0.0.44:8112/api/dashboard/config/acts" \
  -H "Content-Type: application/json" \
  -d '{"data": [...]}'
```

**Réponse** (200):
```json
{
  "success": true,
  "config": "acts",
  "message": "acts.json mis à jour avec succès"
}
```

### GET /api/dashboard/drugs
Récupère la liste des anesthésiques disponibles depuis protocoles_suivi.json.

**Réponse** (200):
```json
{
  "success": true,
  "drugs": [
    {
      "name": "Médétomidine",
      "commercial": "SEDATOR",
      "code_central": "83453",
      "concentration": 1.0,
      "unit": "mg/mL"
    },
    {
      "name": "Butorphanol",
      "commercial": "TORPHASOL",
      "code_central": "55052",
      "concentration": 10.0,
      "unit": "mg/mL"
    }
  ]
}
```

### GET /api/dashboard/presets
Récupère les présets de zones par acte.

**Paramètres**:
- `act_id` (query, optionnel): Filtre par ID d'acte (onde_de_choc, ultrason)

**Exemple**:
```bash
curl "http://10.0.0.44:8112/api/dashboard/presets?act_id=onde_de_choc"
```

**Réponse** (200):
```json
{
  "presets": {
    "onde_de_choc": [
      {
        "zone": "Épaule — Insertion bicipitale",
        "params": {
          "frequence": 4,
          "pression": 1.5,
          "nb_coups": 2000
        }
      }
    ]
  }
}
```

---

## Mémoire Animal (SQLite)

### GET /api/animal-memory/{animal_id}/last-session
Récupère la dernière séance d'un animal pour un acte spécifique.

**Paramètres**:
- `animal_id` (path): ID de l'animal (VetoPartner)
- `act_id` (query): ID de l'acte

**Exemple**:
```bash
curl "http://10.0.0.44:8112/api/animal-memory/21892/last-session?act_id=onde_de_choc"
```

**Réponse** (200) — Séance trouvée:
```json
{
  "found": true,
  "session": {
    "date": "2026-07-10",
    "num_seance": 1,
    "act_name": "Onde de Choc — Traitement",
    "fields": {
      "localisation": "Épaule",
      "frequence": 4,
      "pression": 1.5,
      "nb_coups": 2000
    }
  }
}
```

**Réponse** (200) — Pas de séance:
```json
{
  "found": false
}
```

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
- Ordonnance créée avec delivered=1 (médicaments dispensés immédiatement durant la chirurgie)
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
