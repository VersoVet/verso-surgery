# TODO — verso-surgery

## Complété (Sprint 0)

- [x] Structure initiale du skill créée
- [x] Protocoles anesthésiques codés en JSON (5 protocoles)
- [x] Backend FastAPI complet (animals, protocols, surgeries)
- [x] Manifest.json configuration complète (name, version, resources, etc.)
- [x] API.md documentation complète (tous endpoints)
- [x] ARCHITECTURE.md description modules/structure
- [x] Tests d'intégration (10 tests)
- [x] Health/ready endpoints
- [x] Cron.json avec daily-health-check
- [x] Validation Forge: 13/13 erreurs fixes ✓

## À faire (Sprints futurs)

- [ ] Frontend SPA 4 étapes (recherche, poids, doses, confirmation)
- [ ] Intégration ERP: PATCH /animals/{id}, POST /animals/{id}/ordonnances (attendre erp-connector)
- [ ] Authentification vétérinaire (OAuth/session → vet_id)
- [ ] Export PDF de la fiche chirurgie
- [ ] Store persistant (SQLite → PostgreSQL)
- [ ] Notifications Redis sur validation chirurgie
- [ ] Tests unitaires par module (animals, protocols, surgeries)
- [ ] Pre-commit hooks (ruff, mypy)

## Bugs connus

- Aucun connu au 2026-06-25
- Store en mémoire = données perdues au redémarrage (par design)
