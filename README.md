# Subscription Tracker & Renewal Dashboard

Personal finance dashboard for recurring SaaS and streaming subscriptions. Tracks renewal dates, monthly cash-flow burn, and pause-to-save simulations.

Built for the Quantiphi Machine Learning Engineer vibe coding round.

## Stack

| Layer | Choice |
| --- | --- |
| Frontend | React + Vite + TypeScript |
| Backend | FastAPI |
| Database | SQLite |
| Insights | scikit-learn (local) |
| Extract + chat | Gemini 2.5 Flash (optional) |

Business logic (cost normalization, days-to-renewal, burn, pause) lives on the server. The UI is presentation and interaction only.

## Layout

```
backend/app/          FastAPI app
backend/app/engines/  Cost Uniformity + Date Intersect
backend/app/ml/       Insights + Gemini adapters
backend/data/         SaaS catalog (sklearn training)
frontend/           React dashboard
```

## Run locally

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

- UI: http://localhost:5173
- API health: http://localhost:8000/health
- Vite proxies `/api/*` to the FastAPI process

Copy `.env.example` to `backend/.env` when you add a Gemini key. The app is designed to run without it.

## API (stage 2)

| Method | Path | Notes |
| --- | --- | --- |
| GET | `/health` | liveness |
| POST | `/subscriptions` | create; server computes `monthly_rate` and days-to-renewal |
| GET | `/subscriptions` | list with derived flags |
| GET | `/subscriptions/{id}` | one row |
| PATCH | `/subscriptions/{id}/status` | `{ "status": "active" \| "paused" }` — does **not** delete |
| GET | `/metrics` | burn from **active** rows only; upcoming = renewal in 0–7 days |

Yearly cost is divided by 12 on the server. Paused rows stay in the table and still count toward the upcoming-renewals alert; they drop out of monthly burn.

## Tests

```bash
cd backend
.venv\Scripts\activate
pytest -q
```

## Status

Stage 2: engines + SQLite CRUD + metrics. Dashboard UI is next after this stage is verified.
