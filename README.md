# Hotel Revenue Intelligence

AI-assisted revenue intelligence platform for independent hotels. This repository starts the product described in the PRD with a FastAPI backend, a Next.js dashboard, synthetic hotel demand data, explainable price recommendations, and Dockerized local deployment.

## What Is Included

- Occupancy, ADR, RevPAR, revenue, and market demand forecasts.
- Booking pace variance analytics.
- Explainable pricing recommendations by room type and stay date.
- Competitor price comparison data.
- Multi-property sample data across Bengaluru, Goa, Jaipur, and Mumbai.
- Dynamic dashboard filters for property, room type, and forecast horizon.
- Channel mix and guest segment performance views.
- Interactive dashboard using Next.js, TypeScript, Tailwind CSS, and Recharts.
- FastAPI REST endpoints aligned to the PRD.
- Docker Compose with API, web, PostgreSQL, and Redis services.

## Project Structure

```text
backend/
  app/
    api/                 REST routes
    core/                app configuration
    schemas/             Pydantic API contracts
    services/            synthetic data and revenue intelligence logic
  tests/
frontend/
  app/                   Next.js app router pages
  components/            dashboard UI and charts
  lib/                   API client, types, demo fallback data
docker-compose.yml
```

## Run Locally

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
corepack enable
pnpm install
pnpm run dev
```

Docker:

```bash
docker compose up --build
```

Then open:

- Dashboard: http://localhost:3000
- API docs: http://localhost:8000/docs

## API Endpoints

- `GET /health`
- `POST /forecast`
- `POST /recommend-price`
- `GET /dashboard`
- `GET /booking-pace`
- `GET /market-demand`
- `GET /competitor-analysis`

## Current Implementation Notes

The first implementation uses deterministic synthetic data and transparent business heuristics. That makes the platform demoable immediately while keeping the service layer ready for later SQLAlchemy persistence, XGBoost/LightGBM models, Optuna tuning, and SHAP explainability.
