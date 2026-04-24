# Personal Library

Projet full stack de revue de livres avec :
- Frontend Angular
- Backend FastAPI
- Base PostgreSQL
- Recherche via Google Books API

## Architecture
- `frontend/` : application Angular SPA
- `backend/` : API REST FastAPI avec SQLAlchemy et Pydantic
- `gateway/` : reverse proxy Nginx
- `docker-compose.yml` : orchestration locale
- `.github/workflows/ci.yml` : pipeline CI
- `sonar-project.properties` : configuration SonarQube

## Demarrage local
1. Copier le fichier d'exemple :
   ```powershell
   Copy-Item backend/.env.example backend/.env
   ```
2. Lancer les services :
   ```powershell
   docker compose up --build
   ```
3. Acceder aux applications :
   - Frontend : `http://localhost:4200`
   - Backend : `http://localhost:8000`
   - Gateway : `http://localhost:9000`
   - API docs : `http://localhost:8000/docs`

## Tests et couverture
- Lancer les tests backend avec couverture :
  ```powershell
  docker compose --profile test run --rm backend-tests
  ```
- En CI, le backend produit :
  - `backend/coverage.xml`
  - `backend/pytest-report.xml`

## Preparation SonarQube
- Les sources analysees sont `backend/app`, `frontend/src` et `gateway`
- Les artefacts de build, caches et rapports sont exclus de l'analyse
- La couverture Python est lue depuis `backend/coverage.xml`
- Le rapport de tests Python est lu depuis `backend/pytest-report.xml`

Pour activer l'analyse SonarQube dans GitHub Actions, ajoute ces secrets :
- `SONAR_HOST_URL`
- `SONAR_TOKEN`

## Bonnes pratiques DevOps deja en place
- Variables d'environnement separees via `backend/.env.example`
- Pipeline CI reproductible
- Rapports standard JUnit et Coverage XML
- Exclusions Docker pour reduire le contexte de build
