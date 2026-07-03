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

## 📋 À faire - Priorité haute

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

### Frontend
- [ ] SPA 4 étapes (recherche, poids, doses, confirmation)
- [ ] Intégration protocoles via API
- [ ] Validation stock avant ordonnance

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
