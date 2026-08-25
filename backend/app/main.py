from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.metrics import router as metrics_router
from app.api.subscriptions import router as subscriptions_router
from app.db import init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Subscription Tracker & Renewal Dashboard",
    description="Personal SaaS / streaming spend, renewals, and savings simulation.",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(subscriptions_router)
app.include_router(metrics_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
