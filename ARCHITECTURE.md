# Architecture — verso-surgery

## Vue d'ensemble

Verso Surgery est un service FastAPI pour la gestion des chirurgies vétérinaires avec calcul automatique des doses anesthésiques.

```
Client (Frontend/API)
    ↓
FastAPI (port 8112)
    ├── /dashboard          → Static HTML + JavaScript (5-step wizard)
    ├── /api/dashboard      → DashboardService (proxy erp-connector)
    ├── /api/protocols      → ProtocolService (JSON statique)
    ├── /api/animals        → AnimalService (store mémoire)
    ├── /api/surgeries      → SurgeryService (protocole + doses)
    └── /api/prescriptions  → PrescriptionService → erp-connector (10.0.0.44:8101)
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

### 4. **prescriptions** — Ordonnances via erp-connector

- **Service**: `PrescriptionService`
  - Vérifie disponibilité des médicaments en stock (via erp-connector)
  - Crée ordonnances anesthésiques dans VetoPartner
  - Validation stricte: tous les médicaments doivent être en stock
  - Intégration bidirectionnelle avec erp-connector (10.0.0.44:8101)

- **Routes**:
  - `POST /api/prescriptions/{surgery_id}/validate-stock` — Valider disponibilité
  - `POST /api/prescriptions/{surgery_id}/create-ordonnance` — Créer ordonnance

- **Workflow**:
  1. Créer chirurgie avec doses (via /api/surgeries/)
  2. Valider stock avant ordonnance (via /validate-stock)
  3. Créer ordonnance dans VetoPartner (via /create-ordonnance)
  4. Ordonnance créée avec delivered=1 (médicaments dispensés immédiatement)

### 5. **dashboard** — Interface web 5-step wizard + Configuration

- **Service**: `DashboardService`
  - Proxy vers erp-connector pour RDV, patients, animaux, sites, vétérinaires
  - Utilise la lib `erp-ui-sdk` pour les services (SiteService, VetService, AppointmentService, PatientService)
  - Gestion des consultations
  - Gestion des configurations JSON (acts, protocols, protocoles_suivi, presets)
  - Proxy endpoints: /sites, /vets, /appointments, /search, /animals, /consultations

- **Routes**:
  - `GET /api/dashboard/sites` — Tous les sites vétérinaires (via erp-ui-sdk)
  - `GET /api/dashboard/vets` — Tous les vétérinaires (via erp-ui-sdk)
  - `GET /api/dashboard/appointments?date_from=...&date_to=...&site_id=...` — RDV par date/site/vét (via erp-ui-sdk)
  - `GET /api/dashboard/search?q=` — Recherche patient/animal
  - `GET /api/dashboard/animal/{id}` — Détails animal
  - `GET /api/dashboard/acts` — Charge acts.json (6 actes)
  - `GET /api/dashboard/presets?act_id=` — Charge presets.json par acte
  - `GET /api/dashboard/drugs` — Liste des anesthésiques disponibles (depuis protocoles_suivi.json)
  - `GET /api/dashboard/config/{name}` — Charge config JSON (acts, protocols, protocoles_suivi, presets)
  - `POST /api/dashboard/config/{name}` — Sauvegarde config JSON modifiée
  - `POST /api/dashboard/consultation` — Crée consultation VetoPartner (synthese, motif, veto_id, site_id)
  - `POST /api/dashboard/ordonnance` — Crée ordonnance VetoPartner (animal_id, lignes, veto_id, site_id)
  - `GET /dashboard` → `static/index.html`

- **Frontend** (`static/index.html`):
  - Vanilla JS, ~1100 lignes
  - Light theme (cr-engine style): bg #F9FAFB, primary #4F46E5
  - Utilise composant `ErpPatientSelector` (JavaScript vanilla, via `/static/js/erp-patient-selector.js`)
  - State management: { step, animal, protocol, doses, act, poids, selectedDate, etc. }
  - 5 étapes:
    1. **RDV & Patient** — Sélection via ErpPatientSelector (sites, vétérinaires, date, RDV) ou "continuer sans RDV"
    2. **Patient** — Confirmation patient, affichage fiche, poids éditable
    3. **Acte** — Sélection acte chirurgical, form dynamique (JSON-driven)
    4. **Anesthésie** — Sélection protocole, doses calculées avec fourchettes, checkboxes optional
    5. **Résumé** — Recap complet, création consultation VetoPartner

- **Component** (`static/js/erp-patient-selector.js`):
  - Composant JavaScript vanilla (aucune dépendance)
  - Intègre site selector, vet loader, appointment calendar/list
  - Appelle `/api/dashboard/sites`, `/api/dashboard/vets`, `/api/dashboard/appointments`
  - **Filtre RDV**: Recharge les RDV quand la date ou le site change (rechargement API)
  - Callback `onSelect(patient)` retourne: `{ animal_id, animal_nom, espece, race, poids, client_nom, client_prenom, date_rdv }`

- **Workflow Consultation + Ordonnance** (Étape 5):
  1. Capturer les notes libres du textarea
  2. Créer consultation via `POST /api/dashboard/consultation` avec synthèse complète
  3. Si doses sélectionnées: créer ordonnance via `POST /api/dashboard/ordonnance`
  4. Les doses sélectionnées deviennent des lignes d'ordonnance (designation, notes, type_ligne)

- **Configuration** (`acts.json`):
  - 5 actes configurables: fluoroscopie, ondes de choc, PRP, ODC+PRP, CRI
  - Champs dynamiques: text, number, textarea, select, checkbox
  - Chaque champ: id, label, type, unit, required, default, options

- **Enrichissement** (`protocols.json`):
  - Ajout dose_min, dose_max, optional, code_central
  - Fourchettes: Médétomidine 0.01–0.04, Kétamine 3–8, Butorphanol 0.2–0.4, etc.

### 6. **animal_memory** — Mémoire persistante des traitements

- **Storage**: SQLite (`verso_surgery.db`)
  - Table: `animal_treatments(animal_id, appointment_id, date, act_id, act_name, fields_json)`
  - Index: `(animal_id, act_id)` pour requêtes rapides
  - Idempotent: UNIQUE(appointment_id, act_id)

- **Service**: `AnimalMemoryService`
  - `get_last_session(animal_id, act_id)` — Récupère dernière séance pour un acte
  - `update_animal_memory(animal_id, actes, appointment_id)` — Enregistre les actes après validation

- **Routes**:
  - `GET /api/animal-memory/{animal_id}/last-session?act_id=` — Dernière séance

- **Use Case**: 
  - Vétérinaire fait séance 1 d'onde de choc → enregistré en DB
  - Séance 2 quelques semaines plus tard → précharge les paramètres de séance 1
  - Auto-incrément num_seance (1 → 2 → 3)

### 7. **suivi** — Dashboard de suivi journalier

- **Service**: `SuiviService`
  - Gère le workflow 4 étapes: Arrivée → Anesthésie → Actes → Sortie
  - Persiste état JSON sur disque (/opt/onyx/data/verso-surgery/suivi/{appointment_id}.json)
  - Calcul automatique des doses anesthésiques
  - Génération de compte-rendu structuré (format CRLF)
  - Création ordonnance anesthésique (étape 2)
  - Création consultation VetoPartner (étape 4)
  - Mise à jour animal_memory après validation des actes (non-bloquant)

- **Routes** (Préfixe `/api/suivi`):
  - `GET /protocoles` — Liste des 3 protocoles anesthésiques suivi
  - `GET /tracking` — Trackings du jour (JSON persisté)
  - `GET /tracking/{appointment_id}` — Un tracking spécifique
  - `DELETE /tracking/{appointment_id}` — Reset tracking
  - `POST /arrivee` — Étape 1: créer/mettre à jour tracking
  - `POST /anesthesie` — Étape 2: calcul doses + ordonnance ERP
  - `POST /actes` — Étape 3: enregistrer actes sélectionnés
  - `POST /sortie` — Étape 4: générer CR + consultation ERP
  - `GET /preview/{appointment_id}` — Prévisualiser CR avant validation

- **Modules**:
  - `store.py`: Persistence JSON synchrone (< 100 lignes)
  - `formatter.py`: Formatage CR structuré CRLF (< 80 lignes)
  - `service.py`: Logique métier async (< 300 lignes)
  - `routes.py`: Routes FastAPI (< 200 lignes)

- **Frontend** (`static/suivi.html`):
  - Vanilla JS, ~1400 lignes
  - Timeline avec 4 étapes (dots: pending/done/current)
  - Modal Anesthésie: 3 tabs protocolos, calcul automatique doses, volumes éditables
  - Modal Actes: sélection multi-actes avec formulaires dynamiques + mémoire animal (précharge séance précédente)
  - Modal Sortie: CR éditable avec aperçu avant création
  - Modal Configuration: Édition structurée des 4 catégories (Acts, Protocols, Anesthésie, Présets)
    - Formulaires dynamiques (pas d'édition texte JSON)
    - Gestion des drogues (add/remove) pour protocoles
    - Ajout/suppression d'éléments
    - Validation avant sauvegarde
  - Sélecteur vétérinaire persisté en cookie (365 jours)
  - Auto-refresh toutes les 30s

- **Protocoles** (`protocols.json` + `protocoles_suivi.json`):
  - `protocols.json`: Version générique (code_central: null) — template de base
  - `protocoles_suivi.json`: Version ERP (code_central: réels) — utilisée pour doses + ordonnances
  - 3 protocoles suivi: Sédation légère (SEDATOR+TORPHASOL+PROPOMITOR+ANTIDOR) / Sédation profonde / Anesthésie gazeuse
  - Chaque drogue: dose, dose_min, dose_max, concentration, route, phase, optional, code_central
  - Drugs disponibles: SEDATOR 83453, TORPHASOL 55052, ANTIDOR 23569, PROPOMITOR 14760, KETAMIDOR 42438, etc.

- **Présets par zone** (`presets.json`):
  - Catégories: onde_de_choc, ultrason
  - Chaque zone: nom, paramètres spécifiques (fréquence, pression, nb_coups, intensité, mode, durée)
  - Permet pré-remplissage rapide du formulaire actes (1 clic pour appliquer les params)
  - 5 zones pour ODC, 4 pour ultrason (épaule, carpe, tarse, tendon suspenseur)

- **Workflow**:
  1. **Arrivée**: Créer tracking initial (animal info, poids, client)
  2. **Anesthésie**: Sélectionner protocole, calcul doses, créer ordonnance ERP (lignes avec delivered=1)
  3. **Actes**: Sélectionner actes + remplir formulaires
  4. **Sortie**: Éditer CR, créer consultation ERP avec synthèse

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
  - À ajouter: vet_id depuis session JWT

- **Ordonnances**: Création en "prescription uniquement"
  - À faire: mode "délivré" avec déduction du stock

- **Export**: Pas de PDF/export
  - À faire: générer fiches chirurgie anesthésique

- **Notifications**: Pas de Redis
  - À faire: publier événements sur prescription créée

## Intégrations implémentées

- ✓ **erp-ui-sdk** (lib Python+JavaScript):
  - ErpClient (async HTTP client)
  - SiteService, VetService, AppointmentService, PatientService
  - ErpPatientSelector (composant JavaScript vanilla pour sélection patient/RDV)
  - Utilisée par DashboardService pour les endpoints /sites, /vets, /appointments

- ✓ **erp-connector** (10.0.0.44:8101):
  - Recherche de sites, vétérinaires, RDV via erp-ui-sdk
  - Recherche de médicaments en stock (GET /produits)
  - Création d'ordonnances anesthésiques (POST /animals/{id}/ordonnances)
  - Validation stricte: tous les médicaments doivent être en stock

## Tailles de fichiers

- `src/main.py`: ~250 lignes ✓
- `src/models.py`: ~200 lignes ✓
- `src/modules/protocols/service.py`: ~97 lignes ✓
- `src/modules/animals/service.py`: ~82 lignes ✓
- `src/modules/surgeries/service.py`: ~110 lignes ✓
- `src/modules/prescriptions/service.py`: ~172 lignes ✓
- `src/modules/dashboard/service.py`: ~260 lignes ✓
- `src/modules/dashboard/routes.py`: ~265 lignes (+ endpoints config/drugs) ✓
- `src/modules/animal_memory/store.py`: ~70 lignes ✓
- `src/modules/animal_memory/service.py`: ~70 lignes ✓
- `src/modules/animal_memory/routes.py`: ~35 lignes ✓
- `src/modules/suivi/store.py`: ~100 lignes ✓
- `src/modules/suivi/formatter.py`: ~80 lignes ✓
- `src/modules/suivi/service.py`: ~380 lignes (+ update_animal_memory) ✓
- `src/modules/suivi/routes.py`: ~170 lignes ✓
- `src/modules/suivi/tests/test_suivi.py`: ~10 lignes ✓
- `static/index.html`: ~1225 lignes (vanilla JS, 5-step wizard) ✓
- `static/suivi.html`: ~1450 lignes (vanilla JS, timeline 4 étapes + config modal) ✓
- `static/js/erp-patient-selector.js`: ~290 lignes (vanilla JS, no deps) ✓
- `protocoles_suivi.json`: ~400 lignes ✓
- `protocols.json`: ~320 lignes ✓
- `acts.json`: ~390 lignes ✓
- `presets.json`: ~80 lignes ✓
- Routes: <300 lignes chacune ✓

Tous les fichiers Python < 400 lignes (validations Forge).
Tous les fichiers JSON < 10KB.
JavaScript: vanilla (pas de frameworks), no dependencies.

## Qualité Code

- ✓ Types explicites (mypy)
- ✓ Docstrings Google convention
- ✓ Imports absolus (`from src.xxx`)
- ✓ Pas de credentials en dur
- ✓ httpx async pour HTTP
- ✓ Pydantic pour validation
- ✓ Linting Ruff + format
