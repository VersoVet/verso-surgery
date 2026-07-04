# TODO — verso-surgery

## ✅ Complété (v0.1.0 → v0.1.9)

### Core (Sprint 0)
- [x] Structure initiale du skill créée
- [x] Protocoles anesthésiques codés en JSON (5 protocoles)
- [x] Backend FastAPI complet (animals, protocols, surgeries)
- [x] Manifest.json configuration complète
- [x] API.md documentation complète (tous endpoints)
- [x] ARCHITECTURE.md description modules/structure
- [x] Tests d'intégration (13 tests)
- [x] Health/ready endpoints
- [x] Cron.json avec daily-health-check
- [x] Validation Forge: 13/13 erreurs fixes
- [x] Déploiement v0.1.8 stable

### Ordonnances & ERP (Sprint 1)
- [x] Module prescriptions créé
- [x] Recherche de médicaments en stock (erp-connector API)
- [x] Validation stricte: tous médicaments doivent être en stock
- [x] Création d'ordonnances anesthésiques dans VetoPartner
- [x] Endpoints /validate-stock et /create-ordonnance
- [x] Documentation API.md mise à jour
- [x] ARCHITECTURE.md mise à jour
- [x] Tests pour prescriptions module
- [x] Type checking strict (mypy clean)
- [x] Linting clean (ruff check/format)

## ✅ Complété (v0.1.10 → v0.1.16) — Dashboard 5 étapes

### Dashboard Wizard
- [x] 5-step wizard frontend (RDV → Patient → Anesthésie → Acte → Résumé)
- [x] Light theme (cr-engine style): #F9FAFB background, #4F46E5 primary
- [x] RDV list avec selection depuis erp-connector
- [x] Patient search/details avec poids éditable
- [x] Protocol selection avec dose calculation affichage fourchettes
- [x] Dose overrides (editable fields with recommended + min–max range)
- [x] Optional molecules avec checkboxes (Butorphanol, Méthadone)
- [x] Acts système: 5 actes configurables (fluoroscopie, ondes, PRP, ODC+PRP, CRI)
- [x] Dynamic form rendering depuis acts.json (text, number, textarea, select, checkbox)
- [x] Consultation VetoPartner creation endpoint
- [x] DashboardService proxy vers erp-connector
- [x] StaticFiles mount et /dashboard route
- [x] acts.json et protocols.json enrichissement (dose_min/dose_max/optional/code_central)
- [x] .pre-commit-config.yaml ajouté
- [x] manifest.json avec dashboard config (page, category)
- [x] Validation Forge: VALID (5 warnings)
- [x] Déploiement v0.1.16 successful

## 📋 À faire - Priorité haute

### erp-ui-sdk Library
- [ ] Create `/home/onyx/projects/sdk-dev/erp-ui-sdk/`
- [ ] ErpClient, AppointmentService, PatientService
- [ ] Pydantic models: Animal, Appointment, SearchResult, Client
- [ ] Standardize erp-connector calls across skills
- [ ] Tests et wheel build
- [ ] Déploiement

### Persistence
- [ ] Remplacer store en mémoire par SQLite/PostgreSQL
- [ ] Migrations DB
- [ ] Transactions et rollback

### Authentification
- [ ] JWT tokens pour vet_id
- [ ] Session management
- [ ] RBAC (role-based access control)

### Ordonnances Avancées
- [ ] Mode "délivré" avec déduction du stock
- [ ] Posologie personnalisée par animal
- [ ] Suivi des modifications d'ordonnance
- [ ] Annulation/modification d'ordonnances

## 📋 À faire - Priorité moyenne

### Export & Reporting
- [ ] Génération PDF des fiches de chirurgie
- [ ] Export CSV des historiques
- [ ] Statistiques par protocole/vet

### Notifications
- [ ] Redis pubsub pour événements
- [ ] Alerte stock faible (erp-connector)
- [ ] Notification chirurgie validée

## 📋 À faire - Priorité basse

### Code Quality
- [ ] Pre-commit hooks (ruff, mypy)
- [ ] Tests unitaires par module
- [ ] Coverage report

### Monitoring
- [ ] Métriques Prometheus
- [ ] Logging structuré
- [ ] Alertes SystemD

### Optimisations
- [ ] Cache Redis pour protocoles
- [ ] Pagination des listes
- [ ] Rate limiting

## Known Issues

- ⚠️ Store en mémoire: perte au redémarrage (par design, remplacer par DB)
- ⚠️ Pas d'auth: vet_id doit être validé par frontend
- ⚠️ Ordonnances "prescription uniquement": pas encore de mode délivré

## Warnings Validation Forge

- [W010] TODO.md/ARCHITECTURE.md obsolète (mettre à jour)
- [W999] bandit: binding to all interfaces (src/main.py:201) - port 0.0.0.0 intentionnel
- [W012] Pre-commit hooks manquants
- [W999] dashboard.page/category non définis (optionnels)

## Versions

- **v0.1.0**: Initial scaffold
- **v0.1.8**: Core stable (protocoles, animaux, chirurgies)
- **v0.1.9**: erp-connector intégration avec validation stock
