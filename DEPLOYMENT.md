# Render Deployment

This project is configured for Render using `render.yaml`.

## Current Status

The repository is deployment-ready, but this local folder is not currently a Git repository and there is no authenticated Render session available in this environment. To deploy on Render, push this folder to GitHub and create a Render Blueprint from the repository.

## Services

- `hotel-revenue-intelligence-api`: FastAPI backend, Docker, health check at `/health`.
- `hotel-revenue-intelligence-web`: Next.js dashboard, Docker.
- `hotel-revenue-intelligence-db`: managed PostgreSQL.
- `hotel-revenue-intelligence-redis`: managed Redis.

## Deploy Steps

1. Push this project to a GitHub repository.
2. In Render, choose **New > Blueprint**.
3. Connect the GitHub repository.
4. Select the repo root that contains `render.yaml`.
5. Apply the blueprint.
6. After services are created, confirm these URLs:
   - API: `https://hotel-revenue-intelligence-api.onrender.com`
   - Web: `https://hotel-revenue-intelligence-web.onrender.com`
7. If Render changes either service slug, update:
   - `NEXT_PUBLIC_API_BASE_URL`
   - `HRI_CORS_ORIGINS`

## Important Notes

`NEXT_PUBLIC_API_BASE_URL` is a frontend build-time variable. If the API URL changes, trigger a new frontend deploy after updating that value.

The current backend uses synthetic in-memory data. PostgreSQL and Redis are provisioned for the next stage, when persistence and caching are added.
