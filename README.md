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

## Services Docker Compose
- `gateway` : point d'entree unique de l'application. Il expose `http://localhost:9000`, sert le frontend et redirige les appels `/api/*` vers le backend.
- `frontend` : application Angular. Elle affiche l'interface utilisateur et appelle l'API avec des chemins relatifs pour passer par la gateway.
- `backend` : API FastAPI. Elle contient la logique metier, l'authentification, les routes REST, les services applicatifs et l'acces a la base de donnees.
- `db` : base PostgreSQL. Elle stocke les utilisateurs, les livres, la bibliotheque personnelle, les avis et les donnees de suivi.
- `backend-tests` : service dedie aux tests backend. Il lance `pytest` avec les rapports de couverture et de tests pour la CI.

## Services du Backend
Les services backend sont dans `backend/app/services`. Ils portent la logique metier entre les routes FastAPI et les repositories d'acces aux donnees.

- `AuthService` : gere l'inscription et la connexion. Il verifie l'unicite des emails, hash les mots de passe et valide les identifiants utilisateur.
- `GoogleBooksService` : interroge l'API Google Books. Il normalise les recherches, recupere les details d'un livre, gere les erreurs temporaires et evite les doublons dans les resultats.
- `LibraryService` : gere la bibliotheque personnelle. Il ajoute, liste, met a jour et retire les livres d'un utilisateur, avec validation des statuts de lecture et de la progression en pages.
- `ReviewService` : gere les avis utilisateur. Il verifie que le livre existe et qu'il est bien dans la bibliotheque avant de creer ou mettre a jour une note/commentaire.
- `DashboardService` : calcule les indicateurs du tableau de bord. Il produit les statistiques de lecture, les categories, les formats, les statuts, les priorites, les tags et l'avancement de l'objectif annuel.
- `RecommendationService` : genere les suggestions de lecture. Il se base sur les avis bien notes et la bibliotheque existante, puis utilise Google Books pour proposer des livres non encore sauvegardes.

## Demarrage local
1. Copier le fichier d'exemple :
   ```powershell
   Copy-Item backend/.env.example backend/.env
   ```
2. Lancer les services :
   ```powershell
   docker compose up --build
   ```
3. Acceder a l'application via la gateway :
   - Application : `http://localhost:9000`
   - API proxifiee : `http://localhost:9000/api/v1`
   - API docs : `http://localhost:9000/docs`

La gateway Nginx est le point d'entree unique en local. Le frontend et le backend restent accessibles uniquement sur le reseau Docker interne.

## Tests et couverture
Avant les tests backend, verifier que le fichier d'environnement existe :
```powershell
Copy-Item backend/.env.example backend/.env
```

- Lancer les tests backend avec couverture depuis Docker :
  ```powershell
  docker compose --profile test run --rm backend-tests
  ```

- Lancer les tests frontend Angular avec couverture depuis Docker :
  ```powershell
  docker compose --profile test run --rm frontend-tests
  ```

- Lancer les deux suites de tests depuis Docker :
  ```powershell
  docker compose --profile test run --rm backend-tests
  docker compose --profile test run --rm frontend-tests
  ```

- Construire l'image frontend avant les tests si les dependances ou le Dockerfile ont change :
  ```powershell
  docker compose build frontend
  ```

- Rapports produits pour la CI et SonarQube :
  - `backend/coverage.xml`
  - `backend/pytest-report.xml`
  - `frontend/coverage/personal-library/lcov.info`

## Preparation SonarQube
- Les sources analysees sont `backend/app`, `frontend/src` et `gateway`
- Les artefacts de build, caches et rapports sont exclus de l'analyse
- La couverture Python est lue depuis `backend/coverage.xml`
- Le rapport de tests Python est lu depuis `backend/pytest-report.xml`
- La couverture TypeScript est lue depuis `frontend/coverage/personal-library/lcov.info`

Pour activer l'analyse SonarQube dans GitHub Actions, ajoute ces secrets :
- `SONAR_HOST_URL`
- `SONAR_TOKEN`

## Bonnes pratiques DevOps deja en place
- Variables d'environnement separees via `backend/.env.example`
- Pipeline CI reproductible
- Rapports standard JUnit et Coverage XML
- Exclusions Docker pour reduire le contexte de build
