from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.extract import router as extract_router
from app.api.insights import router as insights_router
from app.api.metrics import router as metrics_router
from app.api.subscriptions import router as subscriptions_router
from app.config import settings
from app.db import init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Subscription Tracker & Renewal Dashboard",
    description="Personal SaaS / streaming spend, renewals, and savings simulation.",
    version="0.3.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(subscriptions_router)
app.include_router(metrics_router)
app.include_router(insights_router)
app.include_router(extract_router)
app.include_router(chat_router)


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse("/docs")


@app.get("/health")
def health() -> dict[str, str | bool]:
    return {"status": "ok", "gemini": bool(settings.gemini_api_key)}
