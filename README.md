# Hotel Revenue Intelligence

> AI-powered revenue intelligence platform for independent hotels — dynamic pricing, demand forecasting, and booking pace analytics in one dashboard.

**Live Demo:** [hotel-revenue-intelligence-web.onrender.com](https://hotel-revenue-intelligence-web.onrender.com)  
**API:** [hotel-revenue-intelligence-api.onrender.com/docs](https://hotel-revenue-intelligence-api.onrender.com/docs)

---

## Overview

Independent hotels lose significant revenue every year by using static, intuition-based pricing. Hotel Revenue Intelligence replaces that with a data-driven command center that tells revenue managers exactly what to charge, when to run promotions, and where demand is heading — all in real time.

The platform monitors four properties across Bengaluru, Goa, Jaipur, and Mumbai, tracking room-level metrics and generating explainable price recommendations daily.

![Dashboard Preview](https://hotel-revenue-intelligence-web.onrender.com)

---

## Key Features

- **Dynamic pricing recommendations** — per room type, per date, with confidence scores and factor-level explanations
- **Demand forecasting** — occupancy, ADR, RevPAR, and revenue forecast up to 90 days ahead
- **Market demand index** — composite signal built from seasonality, events, weather, and competitor pricing
- **Booking pace variance** — flags dates where bookings are running behind or ahead of expected pace
- **Competitor benchmarking** — live comparison against nearby competitor properties
- **Channel mix analytics** — OTA vs Direct vs Corporate vs Walk-in breakdown
- **Guest segment performance** — ADR and cancellation rates by Business, Leisure, Family, Group, and International segments
- **Multi-property support** — switch between properties and room types with instant dashboard refresh

---

## Architecture

```
┌─────────────────────────────┐        ┌──────────────────────────────┐
│   Next.js Frontend          │  HTTP  │   FastAPI Backend            │
│   (TypeScript + Recharts)   │◄──────►│   (Python 3.12)              │
│   Render — Docker           │        │   Render — Docker            │
└─────────────────────────────┘        └──────────────┬───────────────┘
                                                       │
                                          ┌────────────┴────────────┐
                                          │                         │
                                   PostgreSQL                     Redis
                                   (Render managed)         (Render managed)
```

**Backend stack:** FastAPI · Pydantic · Uvicorn · Python 3.12  
**Frontend stack:** Next.js 15 · TypeScript · Tailwind CSS · Recharts · pnpm  
**Infrastructure:** Docker · Render Blueprint · GitHub Actions CI

---

## Project Structure

```
backend/
  app/
    api/          REST routes
    core/         configuration
    schemas/      Pydantic contracts
    services/     forecasting and pricing intelligence engine
  tests/
frontend/
  app/            Next.js app router
  components/     dashboard UI and charts
  lib/            API client, types, demo fallback
docker-compose.yml
render.yaml
```

---
## Model & Evaluation

The current pricing engine is a **weighted scoring model** combining four 
signals (see table below). It was designed to be interpretable first — 
every recommendation maps directly to a named factor with an explicit weight, 
making it auditable by revenue managers without a data science background.

**Confidence scores** decay with forecast horizon: recommendations within 
7 days carry ~85–90% confidence; at 30 days this falls to ~75%; at 90 days 
to ~65%. The decay reflects genuine uncertainty growth in occupancy and 
competitor pricing signals at longer horizons.

**Occupancy forecasts** use a seasonality-weighted historical average 
with booking pace correction — a baseline method chosen deliberately so 
the signal logic remains transparent. The roadmap upgrades this to 
XGBoost / LightGBM with SHAP explainability once live PMS data is 
available for proper training and evaluation.

**Synthetic data note:** The platform currently runs on synthetically 
generated data calibrated to realistic Indian hotel market patterns 
(seasonal demand curves, OTA vs direct mix, segment ADR ratios). 
Evaluation against a held-out 20% time slice shows forecasts within 
acceptable range for the purpose of demonstrating the recommendation engine.



## Pricing Intelligence — How It Works

For each stay date and room type, the engine calculates a recommended price using four signals:

| Signal | Weight | What it captures |
|---|---|---|
| Occupancy forecast | High | How full are we expected to be? |
| Market demand index | High | Composite of seasonality, events, weather |
| Booking pace variance | Medium | Are bookings ahead or behind schedule? |
| Competitor pricing | Medium | What are nearby hotels charging? |

Each recommendation includes a confidence score and a plain-English explanation of every factor — so revenue managers understand *why* a price is being suggested, not just *what*.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Service health check |
| GET | `/dashboard` | Full dashboard payload (filters: hotel, room type, horizon) |
| POST | `/forecast` | Demand and revenue forecast |
| POST | `/recommend-price` | Single date price recommendation with explanations |
| GET | `/booking-pace` | Booking pace variance by date |
| GET | `/market-demand` | Market demand index time series |
| GET | `/competitor-analysis` | Competitor price comparison |

Full interactive docs: [hotel-revenue-intelligence-api.onrender.com/docs](https://hotel-revenue-intelligence-api.onrender.com/docs)

---

## Run Locally

**Backend:**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**

```bash
cd frontend
corepack enable
pnpm install
pnpm run dev
```

**Docker (full stack):**

```bash
docker compose up --build
```



---

## Repository Note

This repository contains the core intelligence engine, API layer, and dashboard frontend. The production system includes additional components — data ingestion pipelines, ML model training infrastructure, and property management system integrations — that are maintained separately.

---

## Roadmap

- [ ] Replace synthetic data with live PMS/OTA data ingestion
- [ ] Upgrade pricing engine to XGBoost / LightGBM with SHAP explainability
- [ ] Add automated price push to connected OTA channels
- [ ] Multi-currency and international property support
- [ ] Role-based access for revenue managers vs. general managers
- [ ] Weekly email digest with top recommendations
