from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user
from app.ml.chat_fallback import reply_from_data
from app.ml.gemini import gemini_enabled, grounded_chat
from app.ml.insights import build_insights
from app.models.user import User
from app.services import subscriptions as svc
from app.services.subscriptions import annotate, compute_metrics

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    reply: str
    source: str


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ChatResponse:
    subs = svc.list_subscriptions(db, user.id)

    def get_metrics():
        return compute_metrics(subs).model_dump()

    def list_subscriptions():
        return [annotate(sub).model_dump(mode="json") for sub in subs]

    def get_insights():
        return build_insights(subs)

    if gemini_enabled():
        try:
            text = grounded_chat(
                payload.message,
                {
                    "get_metrics": get_metrics,
                    "list_subscriptions": list_subscriptions,
                    "get_insights": get_insights,
                },
            )
            if text:
                return ChatResponse(reply=text, source="gemini-2.5-flash")
        except Exception:
            pass
    return ChatResponse(reply=reply_from_data(payload.message, subs), source="intent")
