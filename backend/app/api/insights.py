from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user
from app.ml.insights import build_insights
from app.models.user import User
from app.services import subscriptions as svc

router = APIRouter(tags=["insights"])


@router.get("/insights")
def get_insights(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    return build_insights(svc.list_subscriptions(db, user.id))
