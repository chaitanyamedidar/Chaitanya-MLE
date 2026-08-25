from __future__ import annotations

import json
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.config import settings

MODEL = "gemini-2.5-flash"


class InvoiceDraft(BaseModel):
    name: str = Field(description="Vendor or service name")
    cost: float = Field(description="Plan amount as a positive number")
    billing_cycle: Literal["Monthly", "Yearly"]
    next_renewal_date: str | None = Field(
        default=None, description="ISO date YYYY-MM-DD if present or inferable"
    )
    currency: str = "INR"
    notes: str = ""
    confidence: float = 0.5


def gemini_enabled() -> bool:
    return bool(settings.gemini_api_key)


def _client():
    from google import genai

    return genai.Client(api_key=settings.gemini_api_key)


def extract_invoice(file_bytes: bytes, mime_type: str) -> dict[str, Any]:
    if not gemini_enabled():
        raise RuntimeError("GEMINI_API_KEY is not set")
    from google.genai import types

    client = _client()
    prompt = (
        "Extract a subscription from this invoice, receipt, or billing screenshot. "
        "Return JSON only. billing_cycle must be Monthly or Yearly. "
        "cost is the recurring plan amount (not tax-only). "
        "next_renewal_date must be YYYY-MM-DD and must be today or in the future "
        "(if the invoice date is past, add one billing cycle until it is upcoming)."
    )
    response = client.models.generate_content(
        model=MODEL,
        contents=[
            types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
            prompt,
        ],
        config={
            "response_mime_type": "application/json",
            "response_json_schema": InvoiceDraft.model_json_schema(),
        },
    )
    draft = InvoiceDraft.model_validate_json(response.text or "{}")
    return draft.model_dump()


def grounded_chat(message: str, tools: dict[str, Any]) -> str | None:
    """Return a Gemini reply using in-process tools, or None to fall back."""
    if not gemini_enabled():
        return None
    from google.genai import types

    def get_metrics() -> dict:
        """Current monthly burn and upcoming renewal count. Use for any spend question."""
        return tools["get_metrics"]()

    def list_subscriptions() -> list:
        """List this user's subscriptions with monthly_rate, status, and renewing_soon."""
        return tools["list_subscriptions"]()

    def get_insights() -> dict:
        """Category spend, overlaps, pause recommendations, outliers, cash-flow."""
        return tools["get_insights"]()

    client = _client()
    response = client.models.generate_content(
        model=MODEL,
        contents=message,
        config=types.GenerateContentConfig(
            system_instruction=(
                "You are the Subscription Tracker assistant. "
                "Every number must come from a tool. Never invent burn, dates, or savings. "
                "You are read-only: do not claim you paused or deleted anything. "
                "Be concise."
            ),
            tools=[get_metrics, list_subscriptions, get_insights],
        ),
    )
    text = (response.text or "").strip()
    return text or None
