# Subscription Tracker & Renewal Dashboard

Personal finance dashboard for recurring SaaS and streaming subscriptions. Tracks renewal dates, monthly cash-flow burn, and pause-to-save simulations.

Built for the Quantiphi Machine Learning Engineer vibe coding round.

## Stack

| Layer | Choice |
| --- | --- |
| Frontend | React + Vite + TypeScript |
| Backend | FastAPI |
| Database | SQLite |
| Auth | JWT (`demo@quantiphi.dev` / `Demo@123`) |
| Insights | scikit-learn (local, loaded once) |
| Extract + chat | Gemini 2.5 Flash, with sklearn intent fallback |

All money and date logic lives on the server. Gemini never computes burn, days-to-renewal, or pause math.

## Run

Put `GEMINI_API_KEY` in a repo-root `.env` (never commit it). The app still runs without it.

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

```bash
cd frontend
npm install
npm run dev
```

- UI: http://127.0.0.1:5173
- API: http://127.0.0.1:8000
- Demo login: `demo@quantiphi.dev` / `Demo@123`

## Product rules

- Yearly cost → monthly rate `/ 12` (Cost Uniformity Engine)
- Upcoming alert = renewal in **0–7 days** of server today
- Next renewal on create **cannot be in the past** (date picker `min=today` + server 422)
- Pause greys the row, does **not** delete, and drops that cost from burn
- Insights: category, overlap, pause ranking, high-cost outliers, 90-day cash-flow
- Invoice upload prefills the form; nothing is saved until confirm
- Chat is grounded: Gemini tools or intent fallback, numbers from the ledger

```bash
cd backend
pytest -q
```
